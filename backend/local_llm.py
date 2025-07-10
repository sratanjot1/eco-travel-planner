from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "mistralai/Mistral-7B-Instruct-v0.1"

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

def get_local_plan(prompt: str, max_tokens=400) -> str:
    system_prompt = f"[INST] {prompt.strip()} [/INST]"
    inputs = tokenizer(system_prompt, return_tensors="pt").to(model.device)
    output = model.generate(**inputs, max_new_tokens=max_tokens, temperature=0.7)
    return tokenizer.decode(output[0], skip_special_tokens=True)
