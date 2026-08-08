import time
import logging
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier

logger = logging.getLogger("ModelTraining.Trainer")


class ModelTrainer:
    def __init__(self):
        pass

    def train(
        self,
        algorithm: str,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        hyperparameters: Dict[str, Any],
        random_seed: int = 42
    ) -> Tuple[Any, float]:
        alg_name = algorithm.lower().strip()
        logger.info(f"Initializing algorithm: {alg_name} with random seed {random_seed}...")

        # Initialize the appropriate model based on configuration
        if alg_name == "random_forest" or alg_name == "randomforest":
            # Map hyperparameters with safe fallback defaults
            n_estimators = hyperparameters.get("n_estimators", 100)
            max_depth = hyperparameters.get("max_depth", None)
            min_samples_split = hyperparameters.get("min_samples_split", 2)
            
            model = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                random_state=random_seed,
                n_jobs=-1
            )
        elif alg_name == "xgboost" or alg_name == "xgb":
            n_estimators = hyperparameters.get("n_estimators", 100)
            max_depth = hyperparameters.get("max_depth", 6)
            learning_rate = hyperparameters.get("learning_rate", 0.3)
            
            model = XGBClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=learning_rate,
                random_state=random_seed,
                eval_metric="logloss",
                n_jobs=-1
            )
        elif alg_name == "mlp" or alg_name == "multilayerperceptron":
            hidden_layer_sizes = hyperparameters.get("hidden_layer_sizes", (64, 32))
            max_iter = hyperparameters.get("max_iter", 200)
            alpha = hyperparameters.get("alpha", 0.0001)
            
            model = MLPClassifier(
                hidden_layer_sizes=hidden_layer_sizes,
                max_iter=max_iter,
                alpha=alpha,
                random_state=random_seed
            )
        else:
            error_msg = f"Unsupported algorithm requested: '{algorithm}'. Mandatory algorithms: 'random_forest', 'xgboost'."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Fitting {alg_name} model on features shape: {X_train.shape}...")
        t_start = time.perf_counter()
        try:
            model.fit(X_train, y_train)
        except Exception as e:
            error_msg = f"Training phase failed for algorithm '{algorithm}': {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        duration = time.perf_counter() - t_start
        logger.info(f"Model training successfully completed in {duration:.4f} seconds.")
        
        return model, duration
