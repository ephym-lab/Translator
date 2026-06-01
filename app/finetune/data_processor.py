"""Helper class for data preparation from various formats."""

import json
import random
from typing import List, Tuple


class DataPreprocessor:
    """Helper class to prepare data for fine-tuning from different formats."""
    
    @staticmethod
    def from_csv(csv_path: str, source_col: str, target_col: str) -> Tuple[List[str], List[str]]:
        """Load parallel data from CSV file."""
        import pandas as pd
        df = pd.read_csv(csv_path)
        return df[source_col].tolist(), df[target_col].tolist()
    
    @staticmethod
    def from_json(json_path: str, source_key: str = "source", target_key: str = "target") -> Tuple[List[str], List[str]]:
        """Load parallel data from JSON file.
        
        Supports formats:
        - [{"source": "...", "target": "..."}, ...]
        - [{"src": "...", "tgt": "..."}, ...]
        - {"pairs": [{"source": "...", "target": "..."}, ...]}
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, dict):
            # Try to find the array of pairs
            for key in ['pairs', 'data', 'translations', 'examples']:
                if key in data:
                    data = data[key]
                    break
        
        if not isinstance(data, list):
            raise ValueError(f"Expected JSON array or object with array, got {type(data)}")
        
        # Try different key names
        source_keys = [source_key, 'src', 'source_text', 'input']
        target_keys = [target_key, 'tgt', 'target_text', 'output']
        
        sources = []
        targets = []
        
        for item in data:
            src = None
            tgt = None
            
            # Find source
            for key in source_keys:
                if key in item:
                    src = item[key]
                    break
            
            # Find target
            for key in target_keys:
                if key in item:
                    tgt = item[key]
                    break
            
            if src is None or tgt is None:
                raise ValueError(f"Could not find source/target in item: {item}")
            
            sources.append(src)
            targets.append(tgt)
        
        return sources, targets
    
    @staticmethod
    def from_txt(source_path: str, target_path: str) -> Tuple[List[str], List[str]]:
        """Load parallel data from two text files (one sentence per line)."""
        with open(source_path, 'r', encoding='utf-8') as f:
            sources = [line.strip() for line in f if line.strip()]
        with open(target_path, 'r', encoding='utf-8') as f:
            targets = [line.strip() for line in f if line.strip()]
        
        # Ensure same length
        min_len = min(len(sources), len(targets))
        if len(sources) != len(targets):
            print(f"Warning: Source ({len(sources)}) and target ({len(targets)}) files have different lengths. Truncating to {min_len}.")
        
        return sources[:min_len], targets[:min_len]
    
    @staticmethod
    def augment_data(
        sources: List[str], 
        targets: List[str], 
        augmentation_factor: int = 2
    ) -> Tuple[List[str], List[str]]:
        """Simple data augmentation for small datasets."""
        augmented_sources = sources.copy()
        augmented_targets = targets.copy()
        
        for _ in range(augmentation_factor - 1):
            for src, tgt in zip(sources, targets):
                # Simple augmentation: shuffle words with 10% probability
                if random.random() < 0.1:
                    words = src.split()
                    if len(words) > 2:
                        idx1, idx2 = random.sample(range(len(words)), 2)
                        words[idx1], words[idx2] = words[idx2], words[idx1]
                        augmented_sources.append(' '.join(words))
                        augmented_targets.append(tgt)
        
        return augmented_sources, augmented_targets
    
    @staticmethod
    def validate_data(sources: List[str], targets: List[str], min_length: int = 1, max_length: int = 512) -> Tuple[List[str], List[str]]:
        """Validate and clean data by removing problematic pairs."""
        valid_sources = []
        valid_targets = []
        
        for src, tgt in zip(sources, targets):
            # Check for empty or too short/long sentences
            if not src or not tgt:
                continue
            if len(src.split()) < min_length or len(tgt.split()) < min_length:
                continue
            if len(src) > max_length or len(tgt) > max_length:
                continue
            
            valid_sources.append(src)
            valid_targets.append(tgt)
        
        removed = len(sources) - len(valid_sources)
        if removed > 0:
            print(f"Removed {removed} invalid sentence pairs")
        
        return valid_sources, valid_targets