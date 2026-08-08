"""ComparisonEngine — multi-model benchmark tables and rankings.

Compares all validated models across every metric.
Produces:
  - A structured comparison table (one row per model)
  - Per-metric rankings (1 = best, ties preserved)
  - Per-model strengths, weaknesses, and trade-off notes
  - Radar-ready normalised values (0–1 scale, higher = better for all)

Rules
-----
- Models are never ranked by accuracy alone.
- All rankings are objective — no subjective commentary.
- Normalisation is min-max per metric across the benchmark set.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("Validation.ComparisonEngine")

# Metrics included in the comparison table and rankings
# Listed in significance order — NOT sorted by accuracy
COMPARISON_METRICS = [
    "f1_score",
    "roc_auc",
    "balanced_accuracy",
    "mcc",
    "precision",
    "recall",
    "accuracy",
    "specificity",
    "false_positive_rate",
    "false_negative_rate",
    "log_loss",
    "inference_latency_ms_per_sample",
]

# For these metrics, lower is better (inverted for normalisation)
LOWER_IS_BETTER = {"false_positive_rate", "false_negative_rate", "log_loss",
                   "inference_latency_ms_per_sample"}


def _rank(values: List[Optional[float]], lower_is_better: bool = False) -> List[Optional[int]]:
    """Return 1-based ranks; None values receive None rank."""
    indexed = [(v, i) for i, v in enumerate(values) if v is not None]
    if not indexed:
        return [None] * len(values)
    reverse = not lower_is_better   # higher-is-better → sort descending
    sorted_vals = sorted(indexed, key=lambda x: x[0], reverse=reverse)
    rank_map: Dict[int, int] = {}
    for rank, (_, idx) in enumerate(sorted_vals, start=1):
        rank_map[idx] = rank
    return [rank_map.get(i) for i in range(len(values))]


def _minmax_normalize(values: List[Optional[float]], lower_is_better: bool = False) -> List[Optional[float]]:
    """Min-max normalise to [0, 1]; None values remain None.

    For lower-is-better metrics the scale is inverted so 1 = best.
    """
    valid = [v for v in values if v is not None]
    if len(valid) < 2:
        return [1.0 if v is not None else None for v in values]
    lo, hi = min(valid), max(valid)
    span = hi - lo or 1.0
    result = []
    for v in values:
        if v is None:
            result.append(None)
        else:
            norm = (v - lo) / span
            result.append(round(1.0 - norm if lower_is_better else norm, 4))
    return result


class ComparisonEngine:
    """Generates objective multi-model benchmark comparison."""

    def compare(
        self,
        model_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build a full comparison report from a list of per-model result dicts.

        Parameters
        ----------
        model_results : list of dicts, each containing at minimum:
            model_id, algorithm, version, metrics (dict), quality_gate (dict)

        Returns
        -------
        {
          "comparison_table": [...],
          "rankings":         {...},
          "radar_data":       [...],
          "summary":          {...}
        }
        """
        if not model_results:
            return {
                "comparison_table": [],
                "rankings": {},
                "radar_data": [],
                "summary": {"total_models": 0},
            }

        n = len(model_results)

        # ── Build raw metric columns ──────────────────────────────────────
        metric_cols: Dict[str, List[Optional[float]]] = {m: [] for m in COMPARISON_METRICS}
        for res in model_results:
            m = res.get("metrics") or {}
            for metric in COMPARISON_METRICS:
                val = m.get(metric)
                metric_cols[metric].append(float(val) if val is not None else None)

        # ── Compute rankings ──────────────────────────────────────────────
        rankings: Dict[str, List[Optional[int]]] = {}
        for metric in COMPARISON_METRICS:
            rankings[metric] = _rank(
                metric_cols[metric],
                lower_is_better=(metric in LOWER_IS_BETTER),
            )

        # ── Compute normalised values for radar charts ────────────────────
        normalised: Dict[str, List[Optional[float]]] = {}
        for metric in COMPARISON_METRICS:
            normalised[metric] = _minmax_normalize(
                metric_cols[metric],
                lower_is_better=(metric in LOWER_IS_BETTER),
            )

        # ── Build comparison table ────────────────────────────────────────
        comparison_table: List[Dict[str, Any]] = []
        for i, res in enumerate(model_results):
            row: Dict[str, Any] = {
                "model_id":  res.get("model_id"),
                "algorithm": res.get("algorithm"),
                "version":   res.get("version"),
                "quality_gate_result": (
                    (res.get("quality_gate") or {}).get("result", "UNKNOWN")
                ),
                "metrics": {
                    metric: metric_cols[metric][i]
                    for metric in COMPARISON_METRICS
                },
                "ranks": {
                    metric: rankings[metric][i]
                    for metric in COMPARISON_METRICS
                },
            }
            # Strengths: metrics where this model ranks 1st
            row["strengths"] = [
                m for m in COMPARISON_METRICS
                if rankings[m][i] == 1 and metric_cols[m][i] is not None
            ]
            # Weaknesses: metrics where this model ranks last (among non-None)
            row["weaknesses"] = [
                m for m in COMPARISON_METRICS
                if rankings[m][i] == n and metric_cols[m][i] is not None
                and n > 1
            ]
            # Trade-off note: high throughput but high latency vs precision trade
            tradeoffs = []
            m_map = metric_cols
            if (
                m_map["f1_score"][i] is not None
                and m_map["inference_latency_ms_per_sample"][i] is not None
            ):
                f1_rank  = rankings["f1_score"][i] or n
                lat_rank = rankings["inference_latency_ms_per_sample"][i] or n
                if f1_rank <= 1 and lat_rank > n // 2:
                    tradeoffs.append("Highest F1 but relatively high inference latency.")
                elif lat_rank <= 1 and f1_rank > n // 2:
                    tradeoffs.append("Lowest inference latency but relatively lower F1.")
            row["trade_offs"] = tradeoffs

            comparison_table.append(row)

        # ── Radar-ready normalised data ───────────────────────────────────
        radar_data: List[Dict[str, Any]] = []
        for i, res in enumerate(model_results):
            radar_data.append({
                "model_id":  res.get("model_id"),
                "algorithm": res.get("algorithm"),
                "version":   res.get("version"),
                "normalised_scores": {
                    metric: normalised[metric][i]
                    for metric in COMPARISON_METRICS
                },
            })

        # ── Summary ───────────────────────────────────────────────────────
        passed = [
            r for r in model_results
            if (r.get("quality_gate") or {}).get("result") == "PASSED"
        ]
        summary = {
            "total_models":   n,
            "passed":         len(passed),
            "failed":         n - len(passed),
            "best_f1_model":  _best_model_for(model_results, "f1_score"),
            "best_auc_model": _best_model_for(model_results, "roc_auc"),
            "fastest_model":  _best_model_for(
                model_results, "inference_latency_ms_per_sample",
                lower_is_better=True
            ),
        }

        logger.info(
            "ComparisonEngine complete. %d models compared; %d passed quality gate.",
            n, len(passed)
        )
        return {
            "comparison_table": comparison_table,
            "rankings":         {m: rankings[m] for m in COMPARISON_METRICS},
            "radar_data":       radar_data,
            "summary":          summary,
        }


def _best_model_for(
    model_results: List[Dict[str, Any]],
    metric: str,
    lower_is_better: bool = False,
) -> Optional[str]:
    """Return the model_id of the best-performing model for *metric*."""
    best_id = None
    best_val: Optional[float] = None
    for res in model_results:
        val = (res.get("metrics") or {}).get(metric)
        if val is None:
            continue
        if best_val is None:
            best_val, best_id = float(val), res.get("model_id")
        else:
            if lower_is_better and float(val) < best_val:
                best_val, best_id = float(val), res.get("model_id")
            elif not lower_is_better and float(val) > best_val:
                best_val, best_id = float(val), res.get("model_id")
    return best_id
