"""Example script for fine-tuning NLLB with simple example data."""

import sys
from pathlib import Path

# Add parent directory to path to import from app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.TTTService import NLLBTTTService
from app.finetune.data_processor import DataPreprocessor


def example_fine_tuning():
    """Example of how to fine-tune the model for Swahili-English translation."""
    
    # Initialize the service
    translator = NLLBTTTService()
    
    # Example data (in production, you'd load from files)
    source_sentences = [
        "Hello, how are you?",
        "I would like to book a hotel room.",
        "The weather is beautiful today.",
        "Can you help me find the nearest restaurant?",
        "Thank you for your assistance.",
        "What time does the train arrive?",
        "I need to go to the airport.",
        "How much does this cost?",
        "Where is the bathroom?",
        "I don't understand, please speak slowly."
    ]
    
    target_sentences = [
        "Habari, hujambo?",
        "Ningependa kuchukua chumba cha hoteli.",
        "Hali ya hewa ni nzuri leo.",
        "Je, unaweza kunisaidia kupata mgahawa wa karibu?",
        "Asante kwa msaada wako.",
        "Treni inafika saa ngapi?",
        "Nahitaji kwenda uwanja wa ndege.",
        "Hii inagharimu kiasi gani?",
        "Choo kiko wapi?",
        "Sie lewi, tafadhali sema pole pole."
    ]
    
    # Optional: Validate and augment data
    sources, targets = DataPreprocessor.validate_data(source_sentences, target_sentences)
    if len(sources) < len(source_sentences):
        print(f"After validation: {len(sources)} pairs remain")
    
    # Optionally augment small dataset
    if len(sources) < 100:
        sources, targets = DataPreprocessor.augment_data(sources, targets, augmentation_factor=2)
        print(f"After augmentation: {len(sources)} pairs")
    
    # Prepare training data
    train_dataset = translator.prepare_training_data(
        source_sentences=sources,
        target_sentences=targets,
        source_lang="english",
        target_lang="swahili",
        validation_split=0.2
    )
    
    print(f"Training samples: {len(train_dataset['train'])}")
    print(f"Validation samples: {len(train_dataset['validation'])}")
    
    # Fine-tune the model
    translator.fine_tune(
        train_dataset=train_dataset,
        output_dir="./models/nllb-swahili-finetuned",
        source_lang="english",
        target_lang="swahili",
        num_epochs=3,
        batch_size=2,  # Smaller batch for demonstration
        use_lora=True
    )
    
    # Test the fine-tuned model
    test_sentences = [
        "I need directions to the airport.",
        "What is your name?",
        "The food was delicious."
    ]
    
    print("\nTesting fine-tuned model:")
    for sentence in test_sentences:
        result = translator.translate(sentence, "english", "swahili")
        print(f"English: {sentence}")
        print(f"Swahili: {result}")
        print("-" * 50)


if __name__ == "__main__":
    example_fine_tuning()