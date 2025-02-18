import argparse
import torch
import re
from transformers import AutoModelForCausalLM, AutoTokenizer

def extract_final_answer(response):
    """Aggressive cleanup of reasoning steps"""
    # Split on common answer delimiters
    patterns = [
        r"Answer:\s*(.*)",
        r"ASSISTANT:\s*(.*)",
        r"Final Answer:\s*(.*)",
        r"[\n]+\s*(.*?)(?:\n\n|$)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            clean = match.group(1).strip()
            # Remove any remaining markdown or special tokens
            clean = re.sub(r"<\|.*?\|>|```|\[.*?\]", "", clean)
            return clean
            
    # Fallback: Return last line if all else fails
    return response.split("\n")[-1].strip()

def main():
    parser = argparse.ArgumentParser(description='Strict Answer Chat')
    parser.add_argument('--temp', type=float, default=0.3,  # Lower default temp
                      help='Control randomness (0=strict, 1=creative)')
    parser.add_argument('--model', type=str,
                      default='deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B',
                      help='HF model ID')
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = AutoModelForCausalLM.from_pretrained(args.model).to(device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    tokenizer.pad_token = tokenizer.eos_token

    print(f"Running on {device.upper()} | Temp: {args.temp}")
    print("Type 'quit' to exit\n" + "-"*40)

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']: break
            
            # Force concise answers in the prompt
            prompt = f"{user_input}"
            
            inputs = tokenizer(prompt, return_tensors='pt').to(device)
            outputs = model.generate(
                **inputs,
                max_new_tokens=1000,
                temperature=args.temp,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                no_repeat_ngram_size=3  # Reduce rambling
            )
            
            full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            clean_answer = extract_final_answer(full_response)
            
            print(f"\nAssistant: {clean_answer}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()