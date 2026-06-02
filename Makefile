# ============================================
# NLLB Fine-tuning Commands
# ============================================

.PHONY: finetune-example finetune-csv finetune-json finetune-txt finetune-all
.PHONY: finetune-english-swahili finetune-english-kikuyu finetune-english-somali
.PHONY: finetune-list-models finetune-clean-models finetune-evaluate
.PHONY: finetune-cli finetune-cli-csv finetune-cli-json finetune-cli-txt finetune-cli-example finetune-cli-help
.PHONY: finetune-script-simple finetune-script-csv finetune-script-json finetune-script-txt

# Default fine-tuning settings
FINETUNE_OUTPUT_DIR ?= ./finetuned_models/
FINETUNE_EPOCHS ?= 5
FINETUNE_BATCH_SIZE ?= 4
FINETUNE_VALIDATION_SPLIT ?= 0.1

# Language pair configurations
EN_SWA_OUTPUT := ./finetuned_models/eng_swa_finetuned
EN_KIK_OUTPUT := ./finetuned_models/eng_kik_finetuned
EN_SOM_OUTPUT := ./finetuned_models/eng_som_finetuned
EN_AMA_OUTPUT := ./finetuned_models/eng_ama_finetuned

# ============================================
# CLI Tool Commands
# ============================================

finetune-cli:
	@echo "Running NLLB fine-tuning CLI..."
	uv run python -m app.finetune.cli $(ARGS)

finetune-cli-csv:
	@echo "Running CSV fine-tuning via CLI..."
	@test -n "$(CSV_PATH)" || (echo "Error: CSV_PATH not set. Usage: make finetune-cli-csv CSV_PATH=data.csv SOURCE_COL=en TARGET_COL=sw SOURCE_LANG=english TARGET_LANG=swahili" && exit 1)
	@test -n "$(SOURCE_COL)" || (echo "Error: SOURCE_COL not set" && exit 1)
	@test -n "$(TARGET_COL)" || (echo "Error: TARGET_COL not set" && exit 1)
	@test -n "$(SOURCE_LANG)" || (echo "Error: SOURCE_LANG not set" && exit 1)
	@test -n "$(TARGET_LANG)" || (echo "Error: TARGET_LANG not set" && exit 1)
	uv run python -m app.finetune.cli --mode csv \
		--csv-path $(CSV_PATH) \
		--source-col $(SOURCE_COL) \
		--target-col $(TARGET_COL) \
		--source-lang $(SOURCE_LANG) \
		--target-lang $(TARGET_LANG) \
		--output-dir $(FINETUNE_OUTPUT_DIR) \
		--epochs $(FINETUNE_EPOCHS) \
		--batch-size $(FINETUNE_BATCH_SIZE)

finetune-cli-json:
	@echo "Running JSON fine-tuning via CLI..."
	@test -n "$(JSON_PATH)" || (echo "Error: JSON_PATH not set. Usage: make finetune-cli-json JSON_PATH=data.json SOURCE_LANG=english TARGET_LANG=swahili" && exit 1)
	@test -n "$(SOURCE_LANG)" || (echo "Error: SOURCE_LANG not set" && exit 1)
	@test -n "$(TARGET_LANG)" || (echo "Error: TARGET_LANG not set" && exit 1)
	uv run python -m app.finetune.cli --mode json \
		--json-path $(JSON_PATH) \
		--source-key $(SOURCE_KEY) \
		--target-key $(TARGET_KEY) \
		--source-lang $(SOURCE_LANG) \
		--target-lang $(TARGET_LANG) \
		--output-dir $(FINETUNE_OUTPUT_DIR) \
		--epochs $(FINETUNE_EPOCHS) \
		--batch-size $(FINETUNE_BATCH_SIZE)

finetune-cli-txt:
	@echo "Running TXT fine-tuning via CLI..."
	@test -n "$(SOURCE_TXT)" || (echo "Error: SOURCE_TXT not set. Usage: make finetune-cli-txt SOURCE_TXT=source.txt TARGET_TXT=target.txt SOURCE_LANG=english TARGET_LANG=swahili" && exit 1)
	@test -n "$(TARGET_TXT)" || (echo "Error: TARGET_TXT not set" && exit 1)
	@test -n "$(SOURCE_LANG)" || (echo "Error: SOURCE_LANG not set" && exit 1)
	@test -n "$(TARGET_LANG)" || (echo "Error: TARGET_LANG not set" && exit 1)
	uv run python -m app.finetune.cli --mode txt \
		--source-txt $(SOURCE_TXT) \
		--target-txt $(TARGET_TXT) \
		--source-lang $(SOURCE_LANG) \
		--target-lang $(TARGET_LANG) \
		--output-dir $(FINETUNE_OUTPUT_DIR) \
		--epochs $(FINETUNE_EPOCHS) \
		--batch-size $(FINETUNE_BATCH_SIZE)

finetune-cli-example:
	@echo "Running example fine-tuning via CLI..."
	uv run python -m app.finetune.cli --mode example

finetune-cli-help:
	@echo "Showing CLI help..."
	uv run python -m app.finetune.cli --help

# ============================================
# Direct Script Commands
# ============================================

finetune-script-simple:
	uv run python app/finetune/simple_finetune.py

finetune-script-csv:
	@test -n "$(CSV_PATH)" || (echo "Error: CSV_PATH not set" && exit 1)
	uv run python app/finetune/csv_finetune.py

finetune-script-json:
	@test -n "$(JSON_PATH)" || (echo "Error: JSON_PATH not set" && exit 1)
	uv run python app/finetune/json_finetune.py

finetune-script-txt:
	@test -n "$(SOURCE_TXT)" || (echo "Error: SOURCE_TXT not set" && exit 1)
	uv run python app/finetune/txt_finetune.py

# ============================================
# Basic Fine-tuning Examples
# ============================================

finetune-example:
	@echo "Running example fine-tuning with sample data..."
	uv run python -m app.finetune.simple_finetune

finetune-csv:
	@echo "Fine-tuning from CSV file..."
	@test -n "$(CSV_PATH)" || (echo "Error: CSV_PATH not set. Usage: make finetune-csv CSV_PATH=path/to/file.csv SOURCE_COL=english TARGET_COL=swahili SOURCE_LANG=english TARGET_LANG=swahili" && exit 1)
	@test -n "$(SOURCE_COL)" || (echo "Error: SOURCE_COL not set" && exit 1)
	@test -n "$(TARGET_COL)" || (echo "Error: TARGET_COL not set" && exit 1)
	@test -n "$(SOURCE_LANG)" || (echo "Error: SOURCE_LANG not set" && exit 1)
	@test -n "$(TARGET_LANG)" || (echo "Error: TARGET_LANG not set" && exit 1)
	uv run python -c "from app.finetune.csv_finetune import fine_tune_from_csv; fine_tune_from_csv(csv_path='$(CSV_PATH)', source_col='$(SOURCE_COL)', target_col='$(TARGET_COL)', source_lang='$(SOURCE_LANG)', target_lang='$(TARGET_LANG)', output_dir='$(FINETUNE_OUTPUT_DIR)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true, validation_split=$(FINETUNE_VALIDATION_SPLIT))"

finetune-json:
	@echo "Fine-tuning from JSON file..."
	@test -n "$(JSON_PATH)" || (echo "Error: JSON_PATH not set. Usage: make finetune-json JSON_PATH=path/to/file.json SOURCE_LANG=english TARGET_LANG=swahili" && exit 1)
	@test -n "$(SOURCE_LANG)" || (echo "Error: SOURCE_LANG not set" && exit 1)
	@test -n "$(TARGET_LANG)" || (echo "Error: TARGET_LANG not set" && exit 1)
	uv run python -c "from app.finetune.json_finetune import fine_tune_from_json; fine_tune_from_json(json_path='$(JSON_PATH)', source_lang='$(SOURCE_LANG)', target_lang='$(TARGET_LANG)', source_key='$(SOURCE_KEY)', target_key='$(TARGET_KEY)', output_dir='$(FINETUNE_OUTPUT_DIR)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true, validation_split=$(FINETUNE_VALIDATION_SPLIT))"

finetune-txt:
	@echo "Fine-tuning from text files..."
	@test -n "$(SOURCE_TXT)" || (echo "Error: SOURCE_TXT not set. Usage: make finetune-txt SOURCE_TXT=source.txt TARGET_TXT=target.txt SOURCE_LANG=english TARGET_LANG=swahili" && exit 1)
	@test -n "$(TARGET_TXT)" || (echo "Error: TARGET_TXT not set" && exit 1)
	@test -n "$(SOURCE_LANG)" || (echo "Error: SOURCE_LANG not set" && exit 1)
	@test -n "$(TARGET_LANG)" || (echo "Error: TARGET_LANG not set" && exit 1)
	uv run python -c "from app.finetune.txt_finetune import fine_tune_from_txt; fine_tune_from_txt(source_path='$(SOURCE_TXT)', target_path='$(TARGET_TXT)', source_lang='$(SOURCE_LANG)', target_lang='$(TARGET_LANG)', output_dir='$(FINETUNE_OUTPUT_DIR)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true, validation_split=$(FINETUNE_VALIDATION_SPLIT), augment=$(AUGMENT))"

# ============================================
# Language-Specific Fine-tuning Commands
# ============================================

finetune-english-swahili:
	@echo "Fine-tuning English -> Swahili..."
	@test -n "$(DATA_PATH)" || (echo "Error: DATA_PATH not set" && exit 1)
	@if [ "$(FORMAT)" = "csv" ]; then \
		uv run python -c "from app.finetune.csv_finetune import fine_tune_from_csv; fine_tune_from_csv(csv_path='$(DATA_PATH)', source_col='$(SOURCE_COL)', target_col='$(TARGET_COL)', source_lang='english', target_lang='swahili', output_dir='$(EN_SWA_OUTPUT)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true)"; \
	elif [ "$(FORMAT)" = "json" ]; then \
		uv run python -c "from app.finetune.json_finetune import fine_tune_from_json; fine_tune_from_json(json_path='$(DATA_PATH)', source_lang='english', target_lang='swahili', source_key='$(SOURCE_KEY)', target_key='$(TARGET_KEY)', output_dir='$(EN_SWA_OUTPUT)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true)"; \
	elif [ "$(FORMAT)" = "txt" ]; then \
		uv run python -c "from app.finetune.txt_finetune import fine_tune_from_txt; fine_tune_from_txt(source_path='$(DATA_PATH)', target_path='$(TARGET_PATH)', source_lang='english', target_lang='swahili', output_dir='$(EN_SWA_OUTPUT)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true, augment=$(AUGMENT))"; \
	else \
		echo "Error: FORMAT must be 'csv', 'json', or 'txt'"; \
		exit 1; \
	fi

finetune-english-kikuyu:
	@echo "Fine-tuning English -> Kikuyu..."
	@test -n "$(DATA_PATH)" || (echo "Error: DATA_PATH not set" && exit 1)
	@if [ "$(FORMAT)" = "csv" ]; then \
		uv run python -c "from app.finetune.csv_finetune import fine_tune_from_csv; fine_tune_from_csv(csv_path='$(DATA_PATH)', source_col='$(SOURCE_COL)', target_col='$(TARGET_COL)', source_lang='english', target_lang='kikuyu', output_dir='$(EN_KIK_OUTPUT)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true)"; \
	elif [ "$(FORMAT)" = "json" ]; then \
		uv run python -c "from app.finetune.json_finetune import fine_tune_from_json; fine_tune_from_json(json_path='$(DATA_PATH)', source_lang='english', target_lang='kikuyu', source_key='$(SOURCE_KEY)', target_key='$(TARGET_KEY)', output_dir='$(EN_KIK_OUTPUT)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true)"; \
	elif [ "$(FORMAT)" = "txt" ]; then \
		uv run python -c "from app.finetune.txt_finetune import fine_tune_from_txt; fine_tune_from_txt(source_path='$(DATA_PATH)', target_path='$(TARGET_PATH)', source_lang='english', target_lang='kikuyu', output_dir='$(EN_KIK_OUTPUT)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true, augment=$(AUGMENT))"; \
	else \
		echo "Error: FORMAT must be 'csv', 'json', or 'txt'"; \
		exit 1; \
	fi

finetune-english-somali:
	@echo "Fine-tuning English -> Somali..."
	@test -n "$(DATA_PATH)" || (echo "Error: DATA_PATH not set" && exit 1)
	@if [ "$(FORMAT)" = "csv" ]; then \
		uv run python -c "from app.finetune.csv_finetune import fine_tune_from_csv; fine_tune_from_csv(csv_path='$(DATA_PATH)', source_col='$(SOURCE_COL)', target_col='$(TARGET_COL)', source_lang='english', target_lang='somali', output_dir='$(EN_SOM_OUTPUT)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true)"; \
	elif [ "$(FORMAT)" = "json" ]; then \
		uv run python -c "from app.finetune.json_finetune import fine_tune_from_json; fine_tune_from_json(json_path='$(DATA_PATH)', source_lang='english', target_lang='somali', source_key='$(SOURCE_KEY)', target_key='$(TARGET_KEY)', output_dir='$(EN_SOM_OUTPUT)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true)"; \
	elif [ "$(FORMAT)" = "txt" ]; then \
		uv run python -c "from app.finetune.txt_finetune import fine_tune_from_txt; fine_tune_from_txt(source_path='$(DATA_PATH)', target_path='$(TARGET_PATH)', source_lang='english', target_lang='somali', output_dir='$(EN_SOM_OUTPUT)', num_epochs=$(FINETUNE_EPOCHS), batch_size=$(FINETUNE_BATCH_SIZE), use_lora=true, augment=$(AUGMENT))"; \
	else \
		echo "Error: FORMAT must be 'csv', 'json', or 'txt'"; \
		exit 1; \
	fi

# ============================================
# Model Management
# ============================================

finetune-list-models:
	@echo "Available fine-tuned models:"
	@echo "========================"
	@if [ -d "./finetuned_models" ]; then \
		find ./finetuned_models -maxdepth 2 -type d -name "*finetuned*" | while read dir; do \
			if [ -f "$$dir/config.json" ]; then \
				echo "[OK] $$dir"; \
				if [ -f "$$dir/training_args.bin" ]; then \
					echo "     Has training checkpoint"; \
				fi; \
			fi; \
		done; \
	else \
		echo "No finetuned_models directory found. Run fine-tuning first."; \
	fi

finetune-clean-models:
	@echo "Cleaning fine-tuned models..."
	@read -p "Are you sure you want to delete all models in ./finetuned_models/? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf ./finetuned_models/*; \
		echo "Models cleaned"; \
	else \
		echo "Cancelled"; \
	fi

finetune-clean-specific:
	@echo "Cleaning specific model: $(MODEL_PATH)"
	@test -n "$(MODEL_PATH)" || (echo "Error: MODEL_PATH not set" && exit 1)
	@read -p "Are you sure you want to delete $(MODEL_PATH)? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf $(MODEL_PATH); \
		echo "Model deleted"; \
	else \
		echo "Cancelled"; \
	fi

# ============================================
# Model Evaluation
# ============================================

finetune-evaluate:
	@echo "Evaluating fine-tuned model..."
	@test -n "$(MODEL_PATH)" || (echo "Error: MODEL_PATH not set. Usage: make finetune-evaluate MODEL_PATH=./finetuned_models/eng_swa_finetuned" && exit 1)
	@test -n "$(TEST_FILE)" || (echo "Error: TEST_FILE not set. Provide test sentences file" && exit 1)
	uv run python -c "from app.services.nllb_service import NLLBTTTService; translator = NLLBTTTService(fine_tuned_path='$(MODEL_PATH)'); f = open('$(TEST_FILE)', 'r'); [print(f'Source: {line.strip()}\nTranslation: {translator.translate(line.strip(), \"$(SOURCE_LANG)\", \"$(TARGET_LANG)\")}\n---') for line in f if line.strip()]"

# ============================================
# Batch Fine-tuning
# ============================================

finetune-all:
	@echo "Running all fine-tuning examples..."
	@echo ""
	@echo "1/4: English -> Swahili example"
	@make finetune-example
	@echo ""
	@echo "All fine-tuning examples completed!"

# ============================================
# Utility Commands
# ============================================

finetune-check-gpu:
	@echo "Checking GPU availability..."
	uv run python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU Count: {torch.cuda.device_count()}'); print(f'GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

finetune-check-deps:
	@echo "Checking fine-tuning dependencies..."
	uv run python -c "import importlib; packages = ['transformers', 'torch', 'datasets', 'peft', 'bitsandbytes', 'pandas']; [print(f'[OK] {pkg}') if importlib.util.find_spec(pkg) else print(f'[MISSING] {pkg}') for pkg in packages]"

finetune-help:
	@echo "========================================="
	@echo "NLLB Fine-tuning Commands"
	@echo "========================================="
	@echo ""
	@echo "CLI TOOL COMMANDS (recommended):"
	@echo "  make finetune-cli ARGS='--help'    - Run CLI with custom arguments"
	@echo "  make finetune-cli-example          - Run example via CLI"
	@echo "  make finetune-cli-csv              - Run CSV fine-tuning via CLI"
	@echo "  make finetune-cli-json             - Run JSON fine-tuning via CLI"
	@echo "  make finetune-cli-txt              - Run TXT fine-tuning via CLI"
	@echo "  make finetune-cli-help             - Show CLI help"
	@echo ""
	@echo "FUNCTION COMMANDS:"
	@echo "  make finetune-example              - Run example fine-tuning"
	@echo "  make finetune-csv                  - Fine-tune from CSV file"
	@echo "  make finetune-json                 - Fine-tune from JSON file"
	@echo "  make finetune-txt                  - Fine-tune from text files"
	@echo ""
	@echo "SCRIPT COMMANDS (direct):"
	@echo "  make finetune-script-simple        - Run simple_finetune.py directly"
	@echo "  make finetune-script-csv           - Run csv_finetune.py directly"
	@echo "  make finetune-script-json          - Run json_finetune.py directly"
	@echo "  make finetune-script-txt           - Run txt_finetune.py directly"
	@echo ""
	@echo "LANGUAGE-SPECIFIC:"
	@echo "  make finetune-english-swahili      - Fine-tune English->Swahili"
	@echo "  make finetune-english-kikuyu       - Fine-tune English->Kikuyu"
	@echo "  make finetune-english-somali       - Fine-tune English->Somali"
	@echo ""
	@echo "MODEL MANAGEMENT:"
	@echo "  make finetune-list-models          - List all fine-tuned models"
	@echo "  make finetune-clean-models         - Delete all fine-tuned models"
	@echo "  make finetune-clean-specific       - Delete specific model"
	@echo ""
	@echo "EVALUATION & UTILITIES:"
	@echo "  make finetune-evaluate             - Evaluate a fine-tuned model"
	@echo "  make finetune-check-gpu            - Check GPU availability"
	@echo "  make finetune-check-deps           - Check required packages"
	@echo ""
	@echo "EXAMPLES:"
	@echo ""
	@echo "CLI TOOL EXAMPLES:"
	@echo "  make finetune-cli ARGS='--mode csv --csv-path data.csv --source-col en --target-col sw --source-lang english --target-lang swahili'"
	@echo "  make finetune-cli-csv CSV_PATH=data.csv SOURCE_COL=en TARGET_COL=sw SOURCE_LANG=english TARGET_LANG=swahili"
	@echo "  make finetune-cli-json JSON_PATH=data.json SOURCE_LANG=english TARGET_LANG=swahili"
	@echo "  make finetune-cli-txt SOURCE_TXT=en.txt TARGET_TXT=sw.txt SOURCE_LANG=english TARGET_LANG=swahili"
	@echo "  make finetune-cli-help"
	@echo ""
	@echo "FUNCTION EXAMPLES:"
	@echo "  make finetune-csv CSV_PATH=data.csv SOURCE_COL=en TARGET_COL=sw SOURCE_LANG=english TARGET_LANG=swahili"
	@echo "  make finetune-json JSON_PATH=data.json SOURCE_LANG=english TARGET_LANG=swahili"
	@echo "  make finetune-txt SOURCE_TXT=en.txt TARGET_TXT=sw.txt SOURCE_LANG=english TARGET_LANG=swahili"
	@echo "  make finetune-english-swahili DATA_PATH=data.csv FORMAT=csv SOURCE_COL=en TARGET_COL=sw"
	@echo "  make finetune-evaluate MODEL_PATH=./finetuned_models/eng_swa_finetuned TEST_FILE=test.txt SOURCE_LANG=english TARGET_LANG=swahili"
	@echo ""
	@echo "CONFIGURABLE VARIABLES:"
	@echo "  FINETUNE_EPOCHS=5                 - Number of training epochs"
	@echo "  FINETUNE_BATCH_SIZE=4             - Batch size"
	@echo "  FINETUNE_OUTPUT_DIR=./finetuned_models/  - Output directory"
	@echo "  FINETUNE_VALIDATION_SPLIT=0.1     - Validation split ratio"
	@echo "  AUGMENT=true                      - Enable data augmentation (for txt mode)"
	@echo "  SOURCE_KEY=source                 - JSON source key"
	@echo "  TARGET_KEY=target                 - JSON target key"
	@echo ""