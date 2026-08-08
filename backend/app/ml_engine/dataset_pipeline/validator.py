import logging
import pandas as pd
from typing import Dict, Any, List, Optional

logger = logging.getLogger("DatasetPipeline.Validator")


class DatasetValidator:
    def __init__(self):
        pass

    def validate(self, df: pd.DataFrame, label_column: str = "Label", expected_labels: Optional[List[Any]] = None) -> Dict[str, Any]:
        logger.info("Executing data validation checks...")

        # 1. Verify empty dataset
        if df.empty:
            error_msg = "Dataset is empty (contains 0 rows)."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 2. Count missing values
        missing_counts = df.isnull().sum()
        total_missing = int(missing_counts.sum())

        # 3. Count duplicate rows
        duplicate_rows_count = int(df.duplicated().sum())

        # 4. Check duplicate columns
        duplicate_cols = []
        seen_cols = set()
        for col in df.columns:
            if col in seen_cols:
                duplicate_cols.append(col)
            seen_cols.add(col)
        duplicate_cols_count = len(duplicate_cols)

        # 5. Class distribution check
        class_distribution = {}
        has_label = label_column in df.columns
        if has_label:
            counts = df[label_column].value_counts(dropna=False)
            class_distribution = {str(k): int(v) for k, v in counts.items()}

            # Check invalid labels
            if expected_labels:
                actual_labels = df[label_column].unique()
                invalid_labels = [l for l in actual_labels if l not in expected_labels]
                if invalid_labels:
                    logger.warning(f"Detected unexpected labels: {invalid_labels}")

        # 6. Check for unsupported data types (non-numeric for features)
        unsupported_types = {}
        feature_cols = [c for c in df.columns if c != label_column]
        for col in feature_cols:
            if not pd.api.types.is_numeric_dtype(df[col]):
                unsupported_types[col] = str(df[col].dtype)

        if unsupported_types:
            logger.warning(f"Non-numeric types in feature columns: {unsupported_types}")

        stats = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "total_missing_values": total_missing,
            "duplicate_rows": duplicate_rows_count,
            "duplicate_columns": duplicate_cols_count,
            "class_distribution": class_distribution,
            "unsupported_types_count": len(unsupported_types),
        }

        logger.info(f"Validation statistics compiled: {stats}")
        return stats
