from transformers import AutoModelForCausalLM, AutoTokenizer, DataCollatorForLanguageModeling, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, PeftModel
from datasets import Dataset
import torch
import os

device = None
model = None
tokenizer = None
adapter_dir = "./adapter"

def InitModel():
    global model, tokenizer, device

    modelName = "Qwen/Qwen2.5-1.5B"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = AutoModelForCausalLM.from_pretrained(
        modelName,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        low_cpu_mem_usage=True,
    )

    model.gradient_checkpointing_enable() 
    model.enable_input_require_grads()
    model = model.to(device)

    if os.path.exists(adapter_dir):
        model = PeftModel.from_pretrained(model, adapter_dir)
    else:
        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj"
            ],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        model = get_peft_model(model, lora_config)

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

def TrainModel(texts):
    # Create dataset
    formatted_texts = [f"<|im_start|>user\nCompleta: {t}<|im_end|>\n<|im_start|>assistant\n{t}<|im_end|>" for t in texts]
    dataset = Dataset.from_dict({"text": formatted_texts})

    def TokenizeFunc(samples):
        return tokenizer(samples["text"], truncation=True, max_length=512)

    tokenized = dataset.map(TokenizeFunc, batched=True, remove_columns=["text"])

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=adapter_dir,
        num_train_epochs=1,
        per_device_train_batch_size=2,
        learning_rate=5e-5,
        weight_decay=0.01,
        logging_steps=20,
        fp16=torch.cuda.is_available(),
        save_strategy="no",
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=data_collator,
    )

    trainer.train()

    model.save_pretrained(adapter_dir)

    del texts