from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

device = None
model = None
tokenizer = None

def InitModel():
    global model, tokenizer, device

    modelName = "Qwen/Qwen2.5-1.5B"

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        modelName,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        low_cpu_mem_usage=True,
    )

    model = model.to(device)

    tokenizer = AutoTokenizer.from_pretrained(modelName)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = self.tokenizer.eos_token


def GenerateText(text, maxTokens):
    tokenizer.truncation_side = 'left'

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128 
    ).to(device)

    # Generate text
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=maxTokens,
            temperature=0.8,
            top_p=0.85,
            top_k=30,
            repetition_penalty=1.2,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    promptLen = inputs["input_ids"].shape[1]
    generatedIds = outputs[0][promptLen:]

    return tokenizer.decode(generatedIds, skip_special_tokens=True)
