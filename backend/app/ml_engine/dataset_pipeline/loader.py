import os
import logging
import pandas as pd
from typing import List, Optional

logger = logging.getLogger("DatasetPipeline.Loader")


class DatasetLoader:
    def __init__(self):
        pass

    def load(self, filepath: str, required_columns: Optional[List[str]] = None) -> pd.DataFrame:
        logger.info(f"Starting dataset ingestion from: {filepath}")

        # 1. Validate file existence
        if not os.path.exists(filepath):
            error_msg = f"Dataset file not found: {filepath}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # 2. Check if file is empty
        if os.path.getsize(filepath) == 0:
            error_msg = f"Dataset file is empty: {filepath}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 3. Load CSV files
        try:
            # Load only first 2 rows first to validate format/headers efficiently
            pd.read_csv(filepath, nrows=2)
        except Exception as e:
            error_msg = f"Invalid CSV format or corrupted dataset: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            error_msg = f"Failed to parse dataset CSV: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 4. Check required columns if specified
        if required_columns:
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                error_msg = f"Required columns missing from dataset: {missing_cols}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        logger.info(f"Successfully loaded dataset. Shape: {df.shape}")
        return df
