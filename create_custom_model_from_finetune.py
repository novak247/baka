import os
import zipfile
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from unsloth import FastLanguageModel

def main():
    # ----- Step 1: Define paths and parameters -----
    # Base model name and checkpoint zip path provided by you
    base_model_name = "unsloth/DeepSeek-R1-Distill-Llama-8B"
    zip_path = r"C:/Users/Micha\Downloads/model_checkpoint.zip"  # Provided checkpoint zip file
    lora_checkpoint_dir = r"C:/Users/Micha\Downloads/model_checkpoint"  # Extraction directory

    # Check if the checkpoint has been extracted; if not, extract it
    if not os.path.exists(lora_checkpoint_dir):
        print(f"Extracting {zip_path} to {lora_checkpoint_dir} ...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(lora_checkpoint_dir)
        print("Extraction complete.")
    else:
        print(f"Checkpoint already extracted at: {lora_checkpoint_dir}")
    
    # Set the LoRA checkpoint path to the extracted directory
    lora_checkpoint_path = lora_checkpoint_dir

    # Model loading parameters
    max_seq_length = 2048   # Maximum tokens the model can handle
    dtype = None            # Let unsloth choose the best type (FP16/BF16) automatically
    load_in_4bit = True     # Enable 4-bit quantization for memory efficiency

    # ----- Step 2: Load the base model and tokenizer using unsloth -----
    print("Loading base model and tokenizer from unsloth...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=base_model_name,
        max_seq_length=max_seq_length,
        dtype=dtype,
        load_in_4bit=load_in_4bit,
    )
    print("Base model and tokenizer loaded.")

    # ----- Step 3: Load the LoRA adapter and merge it into the base model -----
    print("Loading LoRA adapter from checkpoint...")
    model = PeftModel.from_pretrained(model, lora_checkpoint_path)
    print("LoRA adapter loaded.")

    print("Merging LoRA weights into the base model...")
    model.merge_and_unload()
    print("Merge complete.")

    # ----- Step 4: Save the merged model and tokenizer locally -----
    merged_model_path = r"C:\Users\Micha\Downloads\merged_model"
    os.makedirs(merged_model_path, exist_ok=True)
    
    print(f"Saving merged model to {merged_model_path} ...")
    model.save_pretrained(merged_model_path)
    tokenizer.save_pretrained(merged_model_path)
    print("Merged model and tokenizer saved.")

    # ----- Step 5: Instructions for converting the merged model for Ollama -----
    print("\nTo convert the merged model for Ollama:")
    print("1. Use a conversion tool/script (e.g., from llama.cpp or Ollama documentation) to convert the Hugging Face model to GGUF format.")
    print(f"   Example command (if using a conversion script):")
    print(f"       python convert-hf-to-ggml.py --model {merged_model_path} --outfile model.gguf")
    print("2. Once converted to GGUF, load your model in Ollama with:")
    print("       ollama load ./model.gguf")
    print("3. Run inference with:")
    print("       ollama run <model_name>")
    print("\nPlease refer to Ollama and llama.cpp documentation for detailed conversion instructions.")

if __name__ == "__main__":
    main()
