import logging
import pandas as pd
from typing import Tuple, Dict
from sklearn.model_selection import train_test_split

logger = logging.getLogger("DatasetPipeline.Splitter")


class DatasetSplitter:
    def __init__(self, train_ratio: float = 0.7, val_ratio: float = 0.15, test_ratio: float = 0.15, seed: int = 42):
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.seed = seed

        # Ensure split proportions sum to approximately 1.0
        total = train_ratio + val_ratio + test_ratio
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Train/Val/Test ratios must sum to 1.0. Given: {train_ratio}, {val_ratio}, {test_ratio}")

    def split(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Tuple[pd.DataFrame, pd.Series]]:
        logger.info(f"Splitting dataset with seed: {self.seed}")

        # Check if stratification is possible
        stratify_y = None
        if len(y.unique()) > 1:
            class_counts = y.value_counts()
            if class_counts.min() >= 2:
                stratify_y = y
                logger.info("Stratification is enabled for the split.")
            else:
                logger.warning("Target class counts are too low to enable stratification.")
        else:
            logger.warning("Only 1 unique class present in target. Stratification disabled.")

        # Split: Train/Val vs Test
        test_size = self.test_ratio
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.seed, stratify=stratify_y
        )

        # Split: Train vs Val from X_train_val
        val_size_adjusted = self.val_ratio / (self.train_ratio + self.val_ratio)
        stratify_train_val = None
        if stratify_y is not None:
            if len(y_train_val.unique()) > 1 and y_train_val.value_counts().min() >= 2:
                stratify_train_val = y_train_val

        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val, test_size=val_size_adjusted, random_state=self.seed, stratify=stratify_train_val
        )

        logger.info(f"Split completed. Train shape: {X_train.shape}, Val shape: {X_val.shape}, Test shape: {X_test.shape}")
        
        return {
            "train": (X_train, y_train),
            "val": (X_val, y_val),
            "test": (X_test, y_test),
        }
