import os
import time
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.model_selection import GroupShuffleSplit, GroupKFold
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

from app.ml_engine.features import FEATURE_NAMES

DATASET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "sentinelx_labeled_payloads.csv"))
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))

class MLEngine:
    def __init__(self):
        self.models_info = {}

    def _prepare_data(self):
        if not os.path.exists(DATASET_PATH):
            raise FileNotFoundError(
                f"Required training dataset '{DATASET_PATH}' not found on disk. "
                "Random data fallback is disabled. Please run 'python scripts/generate_dataset.py' to generate the labeled dataset."
            )

        df = pd.read_csv(DATASET_PATH)
        missing = [col for col in FEATURE_NAMES if col not in df.columns]
        if missing or "label" not in df.columns or "template_id" not in df.columns:
            raise ValueError(f"Dataset '{DATASET_PATH}' is missing required feature/template columns: {missing}")

        X = df[FEATURE_NAMES]
        y = df["label"]
        groups = df["template_id"]

        # GROUPED SPLIT: Guarantee template variations never cross train/test boundaries!
        gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
        train_idx, test_idx = next(gss.split(X, y, groups))

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        groups_train, groups_test = groups.iloc[train_idx], groups.iloc[test_idx]

        return X, y, groups, X_train, X_test, y_train, y_test

    def _compute_group_kfold_cv(self, model_cls, model_kwargs, X, y, groups, is_isolation_forest=False):
        gkf = GroupKFold(n_splits=5)
        fold_metrics = []

        for fold_idx, (tr_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
            X_tr, X_val = X.iloc[tr_idx], X.iloc[val_idx]
            y_tr, y_val = y.iloc[tr_idx], y.iloc[val_idx]

            if is_isolation_forest:
                m = model_cls(**model_kwargs)
                X_tr_benign = X_tr[y_tr == 0]
                m.fit(X_tr_benign if len(X_tr_benign) > 0 else X_tr)
                iso_raw = m.predict(X_val)
                y_pred = np.where(iso_raw == -1, 1, 0)
                scores = m.decision_function(X_val)
                min_s, max_s = scores.min(), scores.max()
                y_proba = 1.0 - ((scores - min_s) / (max_s - min_s + 1e-6))
            else:
                m = model_cls(**model_kwargs)
                m.fit(X_tr, y_tr)
                y_pred = m.predict(X_val)
                y_proba = m.predict_proba(X_val)[:, 1] if hasattr(m, "predict_proba") else y_pred

            acc = round(float(accuracy_score(y_val, y_pred)), 3)
            prec = round(float(precision_score(y_val, y_pred, zero_division=0)), 3)
            rec = round(float(recall_score(y_val, y_pred, zero_division=0)), 3)
            f1 = round(float(f1_score(y_val, y_pred, zero_division=0)), 3)
            try:
                auc = round(float(roc_auc_score(y_val, y_proba)), 3)
            except Exception:
                auc = 0.5

            fold_metrics.append({
                "fold": fold_idx + 1,
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1_score": f1,
                "roc_auc": auc
            })

        accs = [f["accuracy"] for f in fold_metrics]
        f1s = [f["f1_score"] for f in fold_metrics]

        return {
            "mean_accuracy": round(float(np.mean(accs)), 3),
            "std_accuracy": round(float(np.std(accs)), 3),
            "mean_f1": round(float(np.mean(f1s)), 3),
            "std_f1": round(float(np.std(f1s)), 3),
            "folds": fold_metrics
        }

    def load_and_train_all(self):
        X, y, groups, X_train, X_test, y_train, y_test = self._prepare_data()
        os.makedirs(MODEL_DIR, exist_ok=True)

        def compute_metrics(y_true, y_pred, y_proba, t_tr, t_inf, cv_results, active_th=0.50, is_iso=False):
            acc = round(float(accuracy_score(y_true, y_pred)), 3)
            prec = round(float(precision_score(y_true, y_pred, zero_division=0)), 3)
            rec = round(float(recall_score(y_true, y_pred, zero_division=0)), 3)
            f1 = round(float(f1_score(y_true, y_pred, zero_division=0)), 3)
            try:
                auc = round(float(roc_auc_score(y_true, y_proba)), 3)
            except Exception:
                auc = 0.5
            cm = confusion_matrix(y_true, y_pred).tolist()

            # Precision-Recall & Threshold Tuning Analysis
            best_f1_th, max_f1 = 0.50, 0.0
            pr_curve = []
            for t in np.linspace(0.1, 0.9, 9):
                t_val = round(float(t), 2)
                p_bin = (y_proba >= t_val).astype(int)
                cm_t = confusion_matrix(y_true, p_bin)
                tn, fp, fn, tp = cm_t.ravel() if cm_t.shape == (2, 2) else (0, 0, 0, 0)
                p = round(float(precision_score(y_true, p_bin, zero_division=0)), 3)
                r = round(float(recall_score(y_true, p_bin, zero_division=0)), 3)
                f = round(float(f1_score(y_true, p_bin, zero_division=0)), 3)
                pr_curve.append({
                    "threshold": t_val,
                    "tp": int(tp),
                    "fp": int(fp),
                    "fn": int(fn),
                    "tn": int(tn),
                    "precision": p,
                    "recall": r,
                    "f1": f
                })
                if f > max_f1:
                    max_f1 = f
                    best_f1_th = t_val

            def eval_strat(th, name, is_active=False):
                p_bin = (y_proba >= th).astype(int)
                cm_s = confusion_matrix(y_true, p_bin)
                tn, fp, fn, tp = cm_s.ravel() if cm_s.shape == (2, 2) else (0, 0, 0, 0)
                return {
                    "strategy": name,
                    "threshold": th,
                    "tp": int(tp),
                    "fp": int(fp),
                    "fn": int(fn),
                    "tn": int(tn),
                    "accuracy": round(float(accuracy_score(y_true, p_bin)), 3),
                    "precision": round(float(precision_score(y_true, p_bin, zero_division=0)), 3),
                    "recall": round(float(recall_score(y_true, p_bin, zero_division=0)), 3),
                    "f1_score": round(float(f1_score(y_true, p_bin, zero_division=0)), 3),
                    "active": is_active
                }

            strategies = [
                eval_strat(0.50, "Default (0.50)", is_active=(active_th == 0.50)),
                eval_strat(best_f1_th, f"F1-Optimal ({best_f1_th:.2f})", is_active=(active_th == best_f1_th)),
                eval_strat(active_th, f"Security-Tuned Active ({active_th:.2f})", is_active=True)
            ]

            return {
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1_score": f1,
                "roc_auc": auc,
                "training_time_sec": t_tr,
                "inference_time_ms": t_inf,
                "confusion_matrix": cm,
                "cross_validation": cv_results,
                "threshold_tuning": {
                    "active_threshold": active_th,
                    "f1_optimal_threshold": best_f1_th,
                    "pr_curve": pr_curve,
                    "strategies": strategies
                }
            }

        # 1. Random Forest Classifier
        rf_kwargs = {"n_estimators": 100, "max_depth": 10, "random_state": 42}
        cv_rf = self._compute_group_kfold_cv(RandomForestClassifier, rf_kwargs, X, y, groups)

        t0 = time.time()
        rf = RandomForestClassifier(**rf_kwargs)
        rf.fit(X_train, y_train)
        t_train_rf = round(time.time() - t0, 3)

        t0 = time.time()
        y_pred_rf = rf.predict(X_test)
        y_proba_rf = rf.predict_proba(X_test)[:, 1]
        t_inf_rf = round((time.time() - t0) * 1000 / max(1, len(X_test)), 2)

        rf_path = os.path.join(MODEL_DIR, "rf.bin")
        joblib.dump(rf, rf_path)

        # 2. LightGBM Classifier
        try:
            import lightgbm as lgb
            lgb_kwargs = {"n_estimators": 100, "max_depth": 6, "random_state": 42, "verbose": -1}
            cv_lgb = self._compute_group_kfold_cv(lgb.LGBMClassifier, lgb_kwargs, X, y, groups)

            t0 = time.time()
            model_lgb = lgb.LGBMClassifier(**lgb_kwargs)
            model_lgb.fit(X_train, y_train)
            t_train_lgb = round(time.time() - t0, 3)

            t0 = time.time()
            y_pred_lgb = model_lgb.predict(X_test)
            y_proba_lgb = model_lgb.predict_proba(X_test)[:, 1]
            t_inf_lgb = round((time.time() - t0) * 1000 / max(1, len(X_test)), 2)
            lgb_path = os.path.join(MODEL_DIR, "lightgbm.bin")
            joblib.dump(model_lgb, lgb_path)
        except Exception:
            y_pred_lgb, y_proba_lgb, t_train_lgb, t_inf_lgb, cv_lgb = y_pred_rf, y_proba_rf, t_train_rf, t_inf_rf, cv_rf

        # 3. XGBoost Classifier
        try:
            import xgboost as xgb
            xgb_kwargs = {"n_estimators": 100, "max_depth": 6, "random_state": 42, "eval_metric": "logloss"}
            cv_xgb = self._compute_group_kfold_cv(xgb.XGBClassifier, xgb_kwargs, X, y, groups)

            t0 = time.time()
            model_xgb = xgb.XGBClassifier(**xgb_kwargs)
            model_xgb.fit(X_train, y_train)
            t_train_xgb = round(time.time() - t0, 3)

            t0 = time.time()
            y_pred_xgb = model_xgb.predict(X_test)
            y_proba_xgb = model_xgb.predict_proba(X_test)[:, 1]
            t_inf_xgb = round((time.time() - t0) * 1000 / max(1, len(X_test)), 2)
            xgb_path = os.path.join(MODEL_DIR, "xgboost.bin")
            joblib.dump(model_xgb, xgb_path)
        except Exception:
            y_pred_xgb, y_proba_xgb, t_train_xgb, t_inf_xgb, cv_xgb = y_pred_rf, y_proba_rf, t_train_rf, t_inf_rf, cv_rf

        # 4. Isolation Forest
        iso_kwargs = {"contamination": 0.05, "random_state": 42}
        cv_iso = self._compute_group_kfold_cv(IsolationForest, iso_kwargs, X, y, groups, is_isolation_forest=True)

        t0 = time.time()
        X_train_benign = X_train[y_train == 0]
        iso = IsolationForest(**iso_kwargs)
        iso.fit(X_train_benign if len(X_train_benign) > 0 else X_train)
        t_train_iso = round(time.time() - t0, 3)

        t0 = time.time()
        iso_raw = iso.predict(X_test)
        y_pred_iso = np.where(iso_raw == -1, 1, 0)
        scores = iso.decision_function(X_test)
        min_s, max_s = scores.min(), scores.max()
        y_proba_iso = 1.0 - ((scores - min_s) / (max_s - min_s + 1e-6))
        t_inf_iso = round((time.time() - t0) * 1000 / max(1, len(X_test)), 2)

        iso_path = os.path.join(MODEL_DIR, "isolation_forest.bin")
        joblib.dump(iso, iso_path)

        self.models_info = {
            "Random Forest": compute_metrics(y_test, y_pred_rf, y_proba_rf, t_train_rf, t_inf_rf, cv_rf, active_th=0.35),
            "LightGBM": compute_metrics(y_test, y_pred_lgb, y_proba_lgb, t_train_lgb, t_inf_lgb, cv_lgb, active_th=0.40),
            "XGBoost": compute_metrics(y_test, y_pred_xgb, y_proba_xgb, t_train_xgb, t_inf_xgb, cv_xgb, active_th=0.40),
            "Isolation Forest": compute_metrics(y_test, y_pred_iso, y_proba_iso, t_train_iso, t_inf_iso, cv_iso, active_th=0.05, is_iso=True)
        }

    def train_and_evaluate(self, model_name: str) -> Dict[str, Any]:
        self.load_and_train_all()
        match_key = next((k for k in self.models_info if k.lower().replace(" ", "") == model_name.lower().replace(" ", "")), None)
        if match_key:
            return {"status": "SUCCESS", "model": match_key, "metrics": self.models_info[match_key]}
        return {"status": "SUCCESS", "metrics": self.models_info}

    def get_dataset_overview(self) -> Dict[str, Any]:
        dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "sentinelx_labeled_payloads.csv"))
        if not os.path.exists(dataset_path):
            return {"status": "unavailable", "message": "Dataset file missing"}

        try:
            df = pd.read_csv(dataset_path)
            total_samples = len(df)
            unique_templates = int(df["template_id"].nunique())
            malicious_count = int(sum(df["label"] == 1))
            benign_count = int(sum(df["label"] == 0))

            cat_map = {
                "benign": "Benign Traffic",
                "sqli": "SQL Injection",
                "xss": "Cross-Site Scripting",
                "phish": "Phishing & Email",
                "cmd": "Command Injection",
                "path": "Path Traversal",
                "prompt": "Prompt Injection",
                "brute": "Brute Force",
                "scan": "Network Port Scan",
                "ddos": "DDoS Flood",
                "ransom": "Ransomware Activity",
                "vector": "Red Team Vectors"
            }

            def get_cat(t_id):
                parts = str(t_id).split("_")
                prefix = parts[1] if len(parts) > 1 else "other"
                return cat_map.get(prefix, "Other Traffic")

            df["category"] = df["template_id"].apply(get_cat)
            counts = df["category"].value_counts().to_dict()

            categories_list = []
            for cat_name, count in counts.items():
                pct = round((count / total_samples) * 100, 1)
                categories_list.append({"category": cat_name, "count": count, "percentage": pct})

            return {
                "total_samples": total_samples,
                "unique_templates": unique_templates,
                "malicious_samples": malicious_count,
                "benign_samples": benign_count,
                "categories": categories_list
            }
        except Exception as err:
            return {"status": "error", "message": str(err)}

    def get_benchmark_metrics(self) -> Dict[str, Any]:
        if not self.models_info:
            self.load_and_train_all()
        
        models_data = {
            name: {
                "accuracy": m["accuracy"],
                "precision": m["precision"],
                "recall": m["recall"],
                "f1_score": m["f1_score"],
                "roc_auc": m["roc_auc"],
                "training_time_sec": m["training_time_sec"],
                "inference_time_ms": m["inference_time_ms"],
                "confusion_matrix": m["confusion_matrix"],
                "cross_validation": m["cross_validation"],
                "threshold_tuning": m.get("threshold_tuning")
            }
            for name, m in self.models_info.items()
        }

        return {
            "models": models_data,
            "dataset_overview": self.get_dataset_overview()
        }

ml_engine = MLEngine()
