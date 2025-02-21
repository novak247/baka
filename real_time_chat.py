import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
os.environ["HF_HUB_DISABLE_PROGRESS_BAR"] = "0"

from unsloth import FastLanguageModel
from transformers import TextStreamer

# ---------------------------
# 1. Load your model/tokenizer
# ---------------------------
max_seq_length = 2048
dtype = None
load_in_4bit = True

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="novak247/massage_assistant_v1_lora",  # or whatever model you trained
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)
FastLanguageModel.for_inference(model)  # Enable faster inference

# ---------------------------
# 2. Define any prompt style or instructions you want to prepend
#    (Optional: if you want the model to follow some format)
# ---------------------------
train_prompt_style = """Below is an instruction that describes a task for a massage robot, paired with an input that provides further context.
Write a response that generates an executable pipeline in Python using only the provided functions.
Before answering, analyze the task carefully and generate a clear sequence of commands.

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

### Question:
{}

### Response:
{}"""

# ---------------------------
# 3. Create a function to interact in real time
# ---------------------------
def chat_loop():
    """
    Runs an infinite loop in the terminal to chat with the model in real-time.
    Type 'exit' or 'quit' to stop, or press Ctrl+D to exit.
    """
    while True:
        try:
            user_input = input("\nUser: ")
        except EOFError:
            print("\nCtrl+D pressed, exiting chat...")
            break

        if user_input.strip().lower() in ["exit", "quit"]:
            print("Exiting chat...")
            break

        # Format your prompt as needed. For example:
        prompt = train_prompt_style.format(user_input, "")

        # Tokenize
        inputs = tokenizer([prompt], return_tensors="pt").to("cuda")

        # Create a streamer for real-time output
        text_streamer = TextStreamer(
            tokenizer, 
            skip_prompt=True,
            skip_special_tokens=True
        )

        print("Assistant:", end="", flush=True)

        # Generate and stream output
        _ = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            streamer=text_streamer,
            max_new_tokens=100,
            pad_token_id=tokenizer.eos_token_id
        )


# ---------------------------
# 4. Run the chat loop if the script is executed directly
# ---------------------------
if __name__ == "__main__":
    chat_loop()
