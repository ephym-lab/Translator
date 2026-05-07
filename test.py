from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# from huggingface_hub import notebook_login

# notebook_login()
# Load NLLB model
model_name = "facebook/nllb-200-distilled-600M"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Input text
text = "Hello, how are you today?"

# Tokenize input
inputs = tokenizer(text, return_tensors="pt")

# Translate to Swahili
translated_tokens = model.generate(
    **inputs,
    forced_bos_token_id=tokenizer.convert_tokens_to_ids("swh_Latn")
)

# Decode output
result = tokenizer.batch_decode(
    translated_tokens,
    skip_special_tokens=True
)

print("Translated text:")
print(result[0])