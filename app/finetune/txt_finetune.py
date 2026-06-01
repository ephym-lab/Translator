"""Fine-tune NLLB using data from text files."""

import sys
from pathlib import Path

# Add parent directory to path to import from app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.TTTService import NLLBTTTService
from app.finetune.data_processor import DataPreprocessor


def fine_tune_from_txt(
    source_path: str,
    target_path: str,
    source_lang: str,
    target_lang: str,
    output_dir: str = "./models/finetuned",
    num_epochs: int = 5,
    batch_size: int = 4,
    use_lora: bool = True,
    validation_split: float = 0.1,
    augment: bool = False,
    augmentation_factor: int = 2
):
    """Fine-tune NLLB model from parallel text files."""
    
    print(f"Loading data from {source_path} and {target_path}...")
    
    # Load data
    sources, targets = DataPreprocessor.from_txt(source_path, target_path)
    
    print(f"Loaded {len(sources)} sentence pairs")
    
    # Validate data
    sources, targets = DataPreprocessor.validate_data(sources, targets)
    print(f"After validation: {len(sources)} pairs remain")
    
    # Optionally augment data
    if augment and len(sources) < 1000:
        sources, targets = DataPreprocessor.augment_data(sources, targets, augmentation_factor)
        print(f"After augmentation: {len(sources)} pairs")
    
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
    # Example for Kikuyu
    fine_tune_from_txt(
        source_path="kikuyu_sentences.txt",
        target_path="english_sentences.txt",
        source_lang="kikuyu",
        target_lang="english",
        output_dir="./models/kik_eng_finetuned",
        num_epochs=5,
        batch_size=4,
        use_lora=True,
        augment=True  # Enable augmentation for small datasets
    )