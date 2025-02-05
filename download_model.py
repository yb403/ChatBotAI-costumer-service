from transformers import CamembertTokenizer, CamembertModel

# Load the model and tokenizer
tokenizer = CamembertTokenizer.from_pretrained("cache_camembert")
model = CamembertModel.from_pretrained("cache_camembert")

# Test tokenization and model loading
inputs = tokenizer("Bonjour, comment ça va?", return_tensors="pt")
outputs = model(**inputs)
print(outputs)
