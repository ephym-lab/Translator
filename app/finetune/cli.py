"""Command-line interface for fine-tuning NLLB models."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.finetune import (
    fine_tune_from_csv,
    fine_tune_from_json,
    fine_tune_from_txt,
    example_fine_tuning
)


def main():
    parser = argparse.ArgumentParser(description="Fine-tune NLLB translation models")
    parser.add_argument("--mode", choices=["csv", "json", "txt", "example"], required=True)
    
    # Common arguments
    parser.add_argument("--source-lang", default="english", help="Source language")
    parser.add_argument("--target-lang", default="swahili", help="Target language")
    parser.add_argument("--output-dir", default="./models/finetuned", help="Output directory")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size")
    parser.add_argument("--no-lora", action="store_true", help="Disable LoRA (uses more memory)")
    
    # CSV-specific arguments
    parser.add_argument("--csv-path", help="Path to CSV file")
    parser.add_argument("--source-col", default="source", help="Source column name in CSV")
    parser.add_argument("--target-col", default="target", help="Target column name in CSV")
    
    # JSON-specific arguments
    parser.add_argument("--json-path", help="Path to JSON file")
    parser.add_argument("--source-key", default="source", help="Source key in JSON")
    parser.add_argument("--target-key", default="target", help="Target key in JSON")
    
    # TXT-specific arguments
    parser.add_argument("--source-txt", help="Path to source text file")
    parser.add_argument("--target-txt", help="Path to target text file")
    
    args = parser.parse_args()
    
    use_lora = not args.no_lora
    
    if args.mode == "example":
        example_fine_tuning()
    
    elif args.mode == "csv":
        if not args.csv_path:
            print("Error: --csv-path is required for CSV mode")
            sys.exit(1)
        fine_tune_from_csv(
            csv_path=args.csv_path,
            source_col=args.source_col,
            target_col=args.target_col,
            source_lang=args.source_lang,
            target_lang=args.target_lang,
            output_dir=args.output_dir,
            num_epochs=args.epochs,
            batch_size=args.batch_size,
            use_lora=use_lora
        )
    
    elif args.mode == "json":
        if not args.json_path:
            print("Error: --json-path is required for JSON mode")
            sys.exit(1)
        fine_tune_from_json(
            json_path=args.json_path,
            source_lang=args.source_lang,
            target_lang=args.target_lang,
            source_key=args.source_key,
            target_key=args.target_key,
            output_dir=args.output_dir,
            num_epochs=args.epochs,
            batch_size=args.batch_size,
            use_lora=use_lora
        )
    
    elif args.mode == "txt":
        if not args.source_txt or not args.target_txt:
            print("Error: --source-txt and --target-txt are required for TXT mode")
            sys.exit(1)
        fine_tune_from_txt(
            source_path=args.source_txt,
            target_path=args.target_txt,
            source_lang=args.source_lang,
            target_lang=args.target_lang,
            output_dir=args.output_dir,
            num_epochs=args.epochs,
            batch_size=args.batch_size,
            use_lora=use_lora
        )


if __name__ == "__main__":
    main()