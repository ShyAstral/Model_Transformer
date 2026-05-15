from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

device = None
model = None
tokenizer = None

def InitModel():
    global model, tokenizer, device

    modelName = "DeepESP/gpt2-spanish"

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        modelName,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        low_cpu_mem_usage=True,
    )

    # Move to GPU if available
    model = model.to(device)

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(modelName)

    # GPT-2 has no pad token by default; use EOS as pad.
    if tokenizer.pad_token is None:
        tokenizer.pad_token = self.tokenizer.eos_token


def GenerateText(text, maxTokens):
    global model, tokenizer, device

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=16
    ).to(device)

    # Generate text
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=maxTokens,# How many new tokens to generate
            temperature=0.8,         # Creativity (0.7-1.0 is good)
            top_p=0.9,               # Nucleus sampling
            top_k=50,
            repetition_penalty=1.1,  # Reduce repetition
            do_sample=True,          # Sampling instead of greedy
            pad_token_id=tokenizer.eos_token_id
        )

    # Decode only the newly generated tokens (skip the prompt).
    promptLen = inputs["input_ids"].shape[1]
    generatedIds = outputs[0][promptLen:]

    return tokenizer.decode(generatedIds, skip_special_tokens=True)
