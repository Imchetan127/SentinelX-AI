import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger("DatasetPipeline.Metadata")


class MetadataManager:
    def __init__(self, metadata_dir: str = "datasets/metadata"):
        self.metadata_dir = metadata_dir

    def calculate_file_hash(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            return ""
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def generate_and_save(
        self,
        filepaths: Dict[str, str],
        dataset_name: str,
        dataset_version: str,
        preprocessing_version: str,
        row_count: int,
        feature_count: int,
        label_distribution: Dict[str, int],
        validation_stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        logger.info("Generating dataset metadata report...")

        # Calculate checksums for each file split
        file_hashes = {}
        for split, path in filepaths.items():
            if os.path.exists(path):
                file_hashes[split] = self.calculate_file_hash(path)

        metadata = {
            "dataset_name": dataset_name,
            "dataset_version": dataset_version,
            "preprocessing_version": preprocessing_version,
            "ingestion_date": datetime.now(timezone.utc).isoformat(),
            "row_count": row_count,
            "feature_count": feature_count,
            "label_distribution": label_distribution,
            "file_hashes": file_hashes,
            "validation_statistics": validation_stats,
        }

        # Ensure metadata directory exists
        os.makedirs(self.metadata_dir, exist_ok=True)
        meta_filepath = os.path.join(self.metadata_dir, f"{dataset_name}_{dataset_version}_metadata.json")
        
        with open(meta_filepath, "w") as f:
            json.dump(metadata, f, indent=4)

        logger.info(f"Metadata report successfully saved to: {meta_filepath}")
        return metadata
