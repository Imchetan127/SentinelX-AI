import logging
import pandas as pd
from typing import Tuple, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler

logger = logging.getLogger("DatasetPipeline.Transformer")


class FeatureTransformer:
    def __init__(self, scaling_strategy: str = "standard"):
        self.scaling_strategy = scaling_strategy.lower()
        self.scaler = None
        
        if self.scaling_strategy == "standard":
            self.scaler = StandardScaler()
        elif self.scaling_strategy == "minmax":
            self.scaler = MinMaxScaler()
        elif self.scaling_strategy == "none":
            self.scaler = None
        else:
            logger.warning(f"Unknown scaling strategy: '{scaling_strategy}'. Falling back to standard scaling.")
            self.scaler = StandardScaler()

    def normalize_target(self, y: pd.Series) -> pd.Series:
        # Standardize target labels: normal/benign -> 0, attack/malicious -> 1
        normalized_y = y.apply(lambda val: 0 if str(val).strip().upper() in ["BENIGN", "NORMAL", "0"] else 1)
        return normalized_y

    def fit_scaler(self, X_train: pd.DataFrame) -> None:
        if self.scaler is not None:
            logger.info(f"Fitting features scaler using strategy: {self.scaling_strategy}")
            self.scaler.fit(X_train)
        else:
            logger.info("No feature scaling strategy selected.")

    def transform_features(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.scaler is not None:
            # Transform and reconstruct DataFrame to preserve column names
            scaled_array = self.scaler.transform(X)
            scaled_df = pd.DataFrame(scaled_array, columns=X.columns, index=X.index)
            return scaled_df
        return X.copy()

    def split_features_target(self, df: pd.DataFrame, label_column: str = "Label") -> Tuple[pd.DataFrame, pd.Series]:
        logger.info("Separating features from target column...")
        if label_column not in df.columns:
            # If label column not present, features is the whole df, target is None
            return df.copy(), pd.Series()
        
        X = df.drop(columns=[label_column])
        y = df[label_column]
        return X, y
