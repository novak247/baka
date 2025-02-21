import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
os.environ["HF_HUB_DISABLE_PROGRESS_BAR"] = "0"

from unsloth import FastLanguageModel
from transformers import TextStreamer
import torch

# ---------------------------
# 1. Load your model/tokenizer
# ---------------------------
max_seq_length = 2048
dtype = None
load_in_4bit = True

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="novak247/massage_assistant_context_lora",  # or your trained model
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)
FastLanguageModel.for_inference(model)  # Enable faster inference

# ---------------------------
# 2. Define prompt style with context
# ---------------------------
train_prompt_style_context = """Below is a conversation that provides instructions for operating a massage robot. The conversation history provides context to help generate an executable Python pipeline using only the provided functions.
Before answering, carefully consider the conversation history to infer any missing actions.

### Instruction:
You are provided with high-level instructions for operating a massage robot. Create an executable pipeline in Python that structures task execution through a sub-task pipeline. This pipeline should be composed exclusively of the functions listed below in the Capabilities section, arranged in a logical and correct order so that it can be directly executed. Your response should only consist of the pipeline without additional information.

Capabilities:
    start() → Initializes the robot.
    stop() → Stops the robot.
    home() → Moves the robot to the home position.
    [x, y, z] = detect_body_part(part_name) → Detects the specified body part and returns the coordinates.
    move_to([x, y, z]) → Moves the robot to the specified coordinates.
    change_force(mode, value) → Adjusts the massage force based on the specified mode:
        - If mode is 'absolute', then value is any real number, setting the force directly.
        - If mode is 'relative', then value is between -1 and 1, modifying the current force F as:
          F_new = (1 + value) * F
    automatic_massage(part_name) → Automatically massages the specified body part.


### Conversation History:
{}
### Latest User Input:
{}

### Response:
{}"""


# ---------------------------
# 3. Custom Text Streamer to capture output
# ---------------------------
class CapturingTextStreamer(TextStreamer):
    def __init__(self, tokenizer, skip_prompt=True, skip_special_tokens=True):
        super().__init__(tokenizer, skip_prompt=skip_prompt, skip_special_tokens=skip_special_tokens)
        self.generated_text = ""
    def on_token(self, token):
        text = self.tokenizer.decode([token], skip_special_tokens=True)
        print(text, end="", flush=True)
        self.generated_text += text
    def reset(self):
        self.generated_text = ""

# ---------------------------
# 4. Function to trim conversation history by removing full turns from the beginning
# ---------------------------
def trim_history(history_list, max_context_len):
    """
    Given a list of conversation blocks (each block a complete "User: ...\nAssistant: ..." turn),
    remove the earliest blocks until the total tokens (when joined) are within available_token_budget.
    """
    while len(history_list) > max_context_len:
        history_list.pop(0)
    return history_list

# ---------------------------
# 5. Create a function to interact in real time with conversation context and dynamic history trimming
# ---------------------------
def chat_loop():
    """
    Runs an interactive terminal chat session with conversation context.
    The conversation history is maintained as full turns and trimmed by removing whole turns
    if the input token count exceeds the set limit.
    Type 'exit' or 'quit' to stop.
    """
    # We'll maintain conversation history as a list of strings, where each entry is:
    # "User: {user_text}\nAssistant: {assistant_response}"
    conversation_history = []
    
    print("Massage Assistant Terminal with Context and History Trimming.\nType 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("\nUser: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting conversation.")
            break

        if user_input.strip().lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Generate the prompt:
        # First, trim the history if needed
        history_text = trim_history(conversation_history, max_context_len=3)
        prompt = train_prompt_style_context.format(history_text, user_input, "")
        
        # Tokenize the prompt and move to GPU if available
        inputs = tokenizer([prompt], return_tensors="pt")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        inputs = inputs.to(device)
        
        # Create our custom streamer
        text_streamer = CapturingTextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        print("\nAssistant: ", end="", flush=True)
        
        # Generate and stream output (the response part)
        _ = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            streamer=text_streamer,
            max_new_tokens=150,
            pad_token_id=tokenizer.eos_token_id
        )
        
        generated_response = text_streamer.generated_text.strip()
        print("\n")
        
        # Append the new turn as a full block to conversation history
        new_turn = "User: " + user_input + "\n" + "Assistant: " + generated_response
        conversation_history.append(new_turn)

# ---------------------------
# 6. Run the chat loop if executed directly
# ---------------------------
if __name__ == "__main__":
    chat_loop()
