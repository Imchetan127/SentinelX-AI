import logging
import numpy as np
import pandas as pd
from typing import Dict, Any

logger = logging.getLogger("DatasetPipeline.Cleaner")


class DatasetCleaner:
    def __init__(self):
        pass

    def clean(self, df: pd.DataFrame, label_column: str = "Label") -> pd.DataFrame:
        logger.info("Executing dataset cleaning operations...")
        cleaned_df = df.copy()

        # 1. Remove duplicate records
        row_count_before = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        duplicates_removed = row_count_before - len(cleaned_df)
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate rows.")

        # 2. Handle infinite values (replace inf and -inf with NaN)
        feature_cols = [c for c in cleaned_df.columns if c != label_column]
        for col in feature_cols:
            if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                # Replace infinite values with NaN
                inf_mask = np.isinf(cleaned_df[col])
                inf_count = int(inf_mask.sum())
                if inf_count > 0:
                    logger.info(f"Replacing {inf_count} infinite values in column '{col}' with NaN.")
                    cleaned_df.loc[inf_mask, col] = np.nan

        # 3. Fill missing values (NaN) with median of each numeric feature column
        # Median is chosen over mean as it is more robust to outliers in network traffic statistics
        for col in feature_cols:
            if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                null_count = int(cleaned_df[col].isnull().sum())
                if null_count > 0:
                    median_val = cleaned_df[col].median()
                    # If median is NaN (all values were NaN/inf), default to 0.0
                    if pd.isnull(median_val):
                        median_val = 0.0
                    logger.info(f"Filling {null_count} missing values in column '{col}' with median: {median_val}")
                    cleaned_df[col] = cleaned_df[col].fillna(median_val)

        logger.info("Dataset cleaning completed successfully.")
        return cleaned_df
