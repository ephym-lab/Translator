"""Fine-tune NLLB using data from a CSV file."""

import sys
from pathlib import Path

# Add parent directory to path to import from app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.TTTService import NLLBTTTService
from app.finetune.data_processor import DataPreprocessor


def fine_tune_from_csv(
    csv_path: str,
    source_col: str,
    target_col: str,
    source_lang: str,
    target_lang: str,
    output_dir: str = "./models/finetuned",
    num_epochs: int = 5,
    batch_size: int = 4,
    use_lora: bool = True,
    validation_split: float = 0.1
):
    """Fine-tune NLLB model from CSV data."""
    
    print(f"Loading data from {csv_path}...")
    
    # Load data
    sources, targets = DataPreprocessor.from_csv(csv_path, source_col, target_col)
    
    print(f"Loaded {len(sources)} sentence pairs")
    
    # Validate data
    sources, targets = DataPreprocessor.validate_data(sources, targets)
    print(f"After validation: {len(sources)} pairs remain")
    
    # Initialize service
    translator = NLLBTTTService()
    
    # Prepare dataset
    dataset = translator.prepare_training_data(
        source_sentences=sources,
        target_sentences=targets,
        source_lang=source_lang,
        target_lang=target_lang,
        validation_split=validation_split
    )
    
    print(f"Training samples: {len(dataset['train'])}")
    print(f"Validation samples: {len(dataset['validation'])}")
    
    # Fine-tune
    translator.fine_tune(
        train_dataset=dataset,
        output_dir=output_dir,
        source_lang=source_lang,
        target_lang=target_lang,
        num_epochs=num_epochs,
        batch_size=batch_size,
        use_lora=use_lora
    )
    
    print(f"Fine-tuning complete! Model saved to {output_dir}")
    return output_dir


if __name__ == "__main__":
    # Example usage - modify these parameters for your use case
    fine_tune_from_csv(
        csv_path="path/to/your/parallel_corpus.csv",
        source_col="english",
        target_col="swahili",
        source_lang="english",
        target_lang="swahili",
        output_dir="./models/eng_swa_finetuned",
        num_epochs=5,
        batch_size=4,
        use_lora=True
    )