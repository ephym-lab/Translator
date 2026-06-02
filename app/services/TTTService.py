from transformers import (
    AutoTokenizer, AutoModelForSeq2SeqLM, 
    Seq2SeqTrainingArguments, Seq2SeqTrainer, 
    DataCollatorForSeq2Seq, BitsAndBytesConfig
)
from datasets import Dataset, DatasetDict
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from abc import ABC, abstractmethod
import asyncio
from functools import partial
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseTTTService(ABC):
    """Abstract base class for Text-to-Text Transfer Transformer services."""

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str: ...


class NLLBTTTService(BaseTTTService):
    """Offline translation service using Facebook NLLB-200 with fine-tuning support."""

    LANGUAGE_CODES = {
        # East African languages
        "english":  "eng_Latn",
        "swahili":  "swh_Latn",
        "kikuyu":   "kik_Latn",
        "maasai":   "mas_Latn",
        "somali":   "som_Latn",
        "kamba":    "kam_Latn",
        "dholuo":   "luo_Latn",
        "amharic":  "amh_Ethi",
        "oromo":    "gaz_Latn",  # Oromo
        "tigrinya": "tir_Ethi",
        
        # European languages
        "german":      "deu_Latn",
        "french":      "fra_Latn",
        "russian":     "rus_Cyrl",
        "spanish":     "spa_Latn",
        "italian":     "ita_Latn",
        "portuguese":  "por_Latn",

        # Asian languages
        "japanese": "jpn_Jpan",
        "korean":   "kor_Hang",
        "arabic":   "arb_Arab",   
        "bengali":  "ben_Beng",
        "punjabi":  "pan_Guru",
        "urdu":     "urd_Arab",
        "telugu":   "tel_Telu",
        "marathi":  "mar_Deva",
        "tamil":    "tam_Taml",

        # Chinese
        "chinese":              "zho_Hans",
        "chinese_traditional":  "zho_Hant",
    }
    
    def __init__(
        self, 
        model_name: str = "facebook/nllb-200-distilled-600M",
        fine_tuned_path: Optional[str] = None,
        use_quantization: bool = False
    ):
        self.model_name = model_name
        self.fine_tuned_path = fine_tuned_path
        self.use_quantization = use_quantization
        self._model = None
        self._tokenizer = None
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        logger.info(f"Using device: {self._device}")

    def _load_model(self) -> None:
        """Load model with optional fine-tuned weights and quantization."""
        if self._model is not None and self._tokenizer is not None:
            return
            
        logger.info(f"Loading NLLB model: {self.model_name}")
        
        try:
            # Check if we have a fine-tuned model
            if self.fine_tuned_path and Path(self.fine_tuned_path).exists():
                logger.info(f"Loading fine-tuned model from: {self.fine_tuned_path}")
                self._tokenizer = AutoTokenizer.from_pretrained(self.fine_tuned_path)
                
                if self.use_quantization:
                    bnb_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.bfloat16,
                    )
                    self._model = AutoModelForSeq2SeqLM.from_pretrained(
                        self.fine_tuned_path,
                        quantization_config=bnb_config,
                        device_map="auto"
                    )
                else:
                    self._model = AutoModelForSeq2SeqLM.from_pretrained(
                        self.fine_tuned_path
                    ).to(self._device)

                logger.info("Finetuned NLLB model loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading fine-tuned model: {str(e)}")
                self.fine_tuned_path = None
                raise e
            
        else:
            try
                # Load base model
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                
                if self.use_quantization and torch.cuda.is_available():
                    bnb_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.bfloat16,
                    )
                    self._model = AutoModelForSeq2SeqLM.from_pretrained(
                        self.model_name,
                        quantization_config=bnb_config,
                        device_map="auto"
                    )
                else:
                    self._model = AutoModelForSeq2SeqLM.from_pretrained(
                        self.model_name
                    ).to(self._device)
        
                logger.info("NLLB model loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading NLLB model: {str(e)}")
                raise e

    def get_language_code(self, lang: str) -> str:
        normalized = lang.lower().strip()
        code = self.LANGUAGE_CODES.get(normalized)
        if code is None:
            logger.warning(f"Unknown language '{lang}', falling back to English")
            return "eng_Latn"
        return code

    def prepare_training_data(
        self,
        source_sentences: List[str],
        target_sentences: List[str],
        source_lang: str,
        target_lang: str,
        validation_split: float = 0.1
    ) -> DatasetDict:
        """
        Prepare parallel corpus for fine-tuning.
        
        Args:
            source_sentences: List of source language sentences
            target_sentences: List of target language sentences  
            source_lang: Source language name (e.g., "english")
            target_lang: Target language name (e.g., "swahili")
            validation_split: Fraction of data to use for validation
        
        Returns:
            DatasetDict with 'train' and 'validation' splits
        """
        src_code = self.get_language_code(source_lang)
        tgt_code = self.get_language_code(target_lang)
        
        # Create dataset
        data = {
            "translation": [
                {"src": src, "tgt": tgt, "src_lang": src_code, "tgt_lang": tgt_code}
                for src, tgt in zip(source_sentences, target_sentences)
            ]
        }
        
        dataset = Dataset.from_dict(data)
        
        # Split into train/validation
        split_dataset = dataset.train_test_split(test_size=validation_split, seed=42)
        
        return DatasetDict({
            'train': split_dataset['train'],
            'validation': split_dataset['test']
        })
    
    def tokenize_dataset(
        self,
        dataset: DatasetDict,
        max_length: int = 128
    ) -> DatasetDict:
        """Tokenize the dataset for training."""
        
        def tokenize_function(examples):
            inputs = [ex["src"] for ex in examples["translation"]]
            targets = [ex["tgt"] for ex in examples["translation"]]
            src_lang = examples["translation"][0]["src_lang"]
            tgt_lang = examples["translation"][0]["tgt_lang"]
            
            # Set source language for tokenizer
            self._tokenizer.src_lang = src_lang
            
            model_inputs = self._tokenizer(
                inputs,
                text_target=targets,
                max_length=max_length,
                truncation=True,
                padding="max_length"
            )
            return model_inputs
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        return tokenized_dataset
    
    def fine_tune(
        self,
        train_dataset: DatasetDict,
        output_dir: str = "./nllb-finetuned",
        source_lang: str = "english",
        target_lang: str = "swahili",
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-5,
        use_lora: bool = True,
        max_length: int = 128
    ):
        """
        Fine-tune the model on custom data.
        
        Args:
            train_dataset: Prepared DatasetDict with 'train' and 'validation' splits
            output_dir: Where to save the fine-tuned model
            source_lang: Source language name
            target_lang: Target language name
            num_epochs: Number of training epochs
            batch_size: Batch size per device
            learning_rate: Learning rate
            use_lora: Use LoRA for memory-efficient fine-tuning
            max_length: Maximum sequence length
        """
        self._load_model()
        
        src_code = self.get_language_code(source_lang)
        tgt_code = self.get_language_code(target_lang)
        
        # Tokenize the dataset
        tokenized_dataset = self.tokenize_dataset(train_dataset, max_length)
        
        # Apply LoRA if requested
        if use_lora and torch.cuda.is_available():
            logger.info("Applying LoRA for memory-efficient fine-tuning")
            self._model = prepare_model_for_kbit_training(self._model)
            
            lora_config = LoraConfig(
                r=16,
                lora_alpha=32,
                target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
                lora_dropout=0.05,
                bias="none",
                task_type="SEQ_2_SEQ_LM"
            )
            self._model = get_peft_model(self._model, lora_config)
            self._model.print_trainable_parameters()
        
        # Training arguments
        training_args = Seq2SeqTrainingArguments(
            output_dir=output_dir,
            eval_strategy="epoch",
            save_strategy="epoch",
            learning_rate=learning_rate,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            weight_decay=0.01,
            num_train_epochs=num_epochs,
            predict_with_generate=True,
            logging_dir=f"{output_dir}/logs",
            logging_steps=100,
            save_total_limit=2,
            fp16=torch.cuda.is_available(),
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
        )
        
        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            self._tokenizer, 
            model=self._model,
            padding=True
        )
        
        # Initialize trainer
        trainer = Seq2SeqTrainer(
            model=self._model,
            args=training_args,
            train_dataset=tokenized_dataset["train"],
            eval_dataset=tokenized_dataset["validation"],
            processing_class=self._tokenizer,
            data_collator=data_collator,
        )
    
        
        # Start training
        logger.info(f"Starting fine-tuning for {source_lang} → {target_lang}")
        trainer.train()
        
        # Save the fine-tuned model
        logger.info(f"Saving fine-tuned model to {output_dir}")
        trainer.save_model(output_dir)
        self._tokenizer.save_pretrained(output_dir)
        
        # Update the service to use the fine-tuned model
        self.fine_tuned_path = output_dir
        self._model = None  # Force reload of fine-tuned model
        self._load_model()
        
        logger.info("Fine-tuning completed successfully!")
        return output_dir

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using the loaded model."""
        self._load_model()

        src_code = self.get_language_code(source_lang)
        tgt_code = self.get_language_code(target_lang)

        logger.debug(f"Translating [{src_code} → {tgt_code}]: '{text[:50]}...'")

        try:
            self._tokenizer.src_lang = src_code
            inputs = self._tokenizer(text, return_tensors="pt").to(self._device)
            
            with torch.no_grad():
                translated_tokens = self._model.generate(
                    **inputs,
                    forced_bos_token_id=self._tokenizer.convert_tokens_to_ids(tgt_code),
                    max_length=200,
                    num_beams=4,  # Add beam search for better quality
                    temperature=0.7,  # Add temperature for controlled generation
                )
            
            result = self._tokenizer.batch_decode(
                translated_tokens, skip_special_tokens=True
            )
            clean_text = result[0].strip()
            logger.debug(f"Translation result: '{clean_text[:50]}...'")
            return clean_text

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise RuntimeError(f"Translation failed: {e}") from e

    async def translate_async(
        self, text: str, source_lang: str, target_lang: str
    ) -> str:
        """Non-blocking translation for use in FastAPI async routes."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, partial(self.translate, text, source_lang, target_lang)
        )

