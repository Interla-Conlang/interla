from huggingface_hub import hf_hub_download

from model.modeling_m2m_100 import M2M100ForConditionalGeneration
from model.tokenization_small100 import SMALL100Tokenizer

hi_text = "जीवन एक चॉकलेट बॉक्स की तरह है।"
chinese_text = "生活就像一盒巧克力。"

model = M2M100ForConditionalGeneration.from_pretrained("alirezamsh/small100")

# Download the required tokenizer files
vocab_file = hf_hub_download(repo_id="alirezamsh/small100", filename="vocab.json")
spm_file = hf_hub_download(
    repo_id="alirezamsh/small100", filename="sentencepiece.bpe.model"
)

# Create the SMALL100Tokenizer instance with the correct files
tokenizer = SMALL100Tokenizer(vocab_file=vocab_file, spm_file=spm_file)

# translate Hindi to French
tokenizer.tgt_lang = "fr"
encoded_hi = tokenizer(hi_text, return_tensors="pt")
generated_tokens = model.generate(**encoded_hi)  # type: ignore
result_hi = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
print(f"Hindi to French: {result_hi}")
# => "La vie est comme une boîte de chocolat."

# translate Chinese to English
tokenizer.tgt_lang = "en"
encoded_zh = tokenizer(chinese_text, return_tensors="pt")
generated_tokens = model.generate(**encoded_zh)  # type: ignore
result_zh = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
print(f"Chinese to English: {result_zh}")
# => "Life is like a box of chocolate."

print()