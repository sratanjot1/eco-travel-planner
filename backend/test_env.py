from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.1",
    torch_dtype=torch.float16,
    device_map="auto"
)

prompt = "Suggest a 3-day eco-friendly travel itinerary for a trip from Delhi to Manali."
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

output = model.generate(
    **inputs,
    max_new_tokens=300,
    do_sample=True,
    top_p=0.95,
    temperature=0.8
)

print(tokenizer.decode(output[0], skip_special_tokens=True))
