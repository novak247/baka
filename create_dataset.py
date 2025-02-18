import json
import random

# ------------------------------
# Helper Functions
# ------------------------------
def maybe_add_ending(text):
    """
    With a 50% chance, adds punctuation ('.', '!', or '...') to the end of text.
    """
    text = text.rstrip(".!?")
    if random.random() < 0.5:
        punctuation = random.choice([".", "!", "..."])
        return text + punctuation
    else:
        return text

def maybe_append_noise(text):
    """
    With a 30% chance, appends an extra, unsupported command (noise) to the text.
    """
    noise_phrases = [
        " and also check the battery level",
        " and then report the temperature",
        " and verify the system status",
        " and log the current time",
        " and update diagnostics"
    ]
    if random.random() < 0.3:
        noise = random.choice(noise_phrases)
        text += noise
    return text

def random_coordinates():
    return [random.randint(-20, 20), random.randint(-20, 20), random.randint(-20, 20)]

def random_body_part():
    return random.choice([
        "lower back", "shoulders", "neck", "arms", "legs", "head",
        "chest", "stomach", "hips", "knees", "elbows", "wrists", "feet", "calves", "forearms"
    ])

def randomize_case(text):
    """
    Randomly returns the input text in lowercase, uppercase, or capitalized.
    """
    options = [text.lower(), text.upper(), text.capitalize()]
    return random.choice(options)

# ------------------------------
# Synonym Lists
# ------------------------------
start_synonyms = ["Start", "Initiate", "Activate", "Power on"]
stop_synonyms = ["Shut down", "Turn off", "Deactivate", "Stop"]
home_synonyms = ["Return to the home position", "Reset to the default position", "Go to home", "Move to home position"]
detect_synonyms = ["Detect", "Identify", "Locate", "Find"]
move_synonyms = ["Move to position", "Navigate to", "Go to", "Proceed to"]
increase_synonyms = ["Increase", "Boost", "Raise", "Enhance"]
decrease_synonyms = ["Reduce", "Lower", "Decrease", "Diminish"]
set_synonyms = ["Set", "Adjust", "Configure", "Establish"]
force_nouns = ["massage intensity", "massage pressure", "force level"]
auto_massage_synonyms = ["Start automatic massage", "Begin auto massage", "Initiate automatic massage", "Activate auto massage"]

# ------------------------------
# Command Generator Functions
# Each returns a tuple: (instruction_text, pipeline_steps_list)
# ------------------------------
def cmd_start():
    syn = random.choice(start_synonyms)
    templates = [
        "{syn} the massage robot",
        "Could you {syn_lower} the massage robot",
        "Please {syn_lower} the massage robot",
        "I would like you to {syn_lower} the massage robot"
    ]
    text = random.choice(templates).format(syn=syn, syn_lower=syn.lower())
    text = maybe_add_ending(text)
    text = maybe_append_noise(text)
    pipeline = ["start()"]
    return text, pipeline

def cmd_stop():
    syn = random.choice(stop_synonyms)
    templates = [
        "{syn} the massage robot",
        "Could you {syn_lower} the massage robot",
        "Please {syn_lower} the massage robot",
        "I would like you to {syn_lower} the massage robot"
    ]
    text = random.choice(templates).format(syn=syn, syn_lower=syn.lower())
    text = maybe_add_ending(text)
    text = maybe_append_noise(text)
    pipeline = ["stop()"]
    return text, pipeline

def cmd_home():
    syn = random.choice(home_synonyms)
    templates = [
        "{syn}",
        "Please {syn_lower}",
        "Could you {syn_lower}"
    ]
    text = random.choice(templates).format(syn=syn, syn_lower=syn.lower())
    text = maybe_add_ending(text)
    text = maybe_append_noise(text)
    pipeline = ["home()"]
    return text, pipeline

def cmd_detect():
    bp = random_body_part()
    bp_variant = randomize_case(bp)
    syn = random.choice(detect_synonyms)
    templates = [
        "{syn} my {bp}",
        "Can you {syn_lower} my {bp}?",
        "Please {syn_lower} my {bp}",
        "I need you to {syn_lower} my {bp}"
    ]
    text = random.choice(templates).format(syn=syn, syn_lower=syn.lower(), bp=bp_variant)
    text = maybe_add_ending(text)
    text = maybe_append_noise(text)
    pipeline = [f"[x, y, z] = detect_body_part('{bp}')"]
    return text, pipeline

def cmd_move():
    # 70% chance to target a body part; 30% chance to use coordinates.
    if random.random() < 0.7:
        bp = random_body_part()
        bp_variant = randomize_case(bp)
        syn = random.choice(move_synonyms)
        templates = [
            "{syn} to my {bp}",
            "Could you {syn_lower} to my {bp}?",
            "Please {syn_lower} to my {bp}",
            "I need you to {syn_lower} to my {bp}"
        ]
        text = random.choice(templates).format(syn=syn, syn_lower=syn.lower(), bp=bp_variant)
        text = maybe_add_ending(text)
        text = maybe_append_noise(text)
        # If the target is a body part, first detect it, then move.
        pipeline = [f"[x, y, z] = detect_body_part('{bp}')", "move_to([x, y, z])"]
    else:
        coords = random_coordinates()
        syn = random.choice(move_synonyms)
        templates = [
            "{syn} {coords}",
            "Could you {syn_lower} {coords}?",
            "Please {syn_lower} {coords}",
            "I need you to {syn_lower} {coords}"
        ]
        text = random.choice(templates).format(syn=syn, syn_lower=syn.lower(), coords=coords)
        text = maybe_add_ending(text)
        text = maybe_append_noise(text)
        pipeline = [f"move_to({coords})"]
    return text, pipeline

def cmd_change_force_relative():
    percentage = random.randint(10, 50)
    if random.random() < 0.5:
        verb = random.choice(decrease_synonyms)
        value = -percentage / 100.0
    else:
        verb = random.choice(increase_synonyms)
        value = percentage / 100.0
    noun = random.choice(force_nouns)
    templates = [
        "{verb} {noun} by {perc}%",
        "Could you {verb_lower} {noun} by {perc}%",
        "Please {verb_lower} {noun} by {perc}%",
        "I would like you to {verb_lower} {noun} by {perc}%"
    ]
    text = random.choice(templates).format(verb=verb, verb_lower=verb.lower(), noun=noun, perc=percentage)
    text = maybe_add_ending(text)
    text = maybe_append_noise(text)
    pipeline = [f"change_force('relative', {value})"]
    return text, pipeline

def cmd_change_force_absolute():
    value = random.uniform(0.1, 1.0)
    percentage = int(value * 100)
    verb = random.choice(set_synonyms)
    noun = random.choice(force_nouns)
    templates = [
        "{verb} {noun} to {perc}%",
        "Could you {verb_lower} {noun} to {perc}%",
        "Please {verb_lower} {noun} to {perc}%",
        "I want you to {verb_lower} {noun} to {perc}%"
    ]
    text = random.choice(templates).format(verb=verb, verb_lower=verb.lower(), noun=noun, perc=percentage)
    text = maybe_add_ending(text)
    text = maybe_append_noise(text)
    pipeline = [f"change_force('absolute', {value:.2f})"]
    return text, pipeline

def cmd_automatic_massage():
    bp = random_body_part()
    bp_variant = randomize_case(bp)
    syn = random.choice(auto_massage_synonyms)
    templates = [
        "{syn} for my {bp}",
        "Could you {syn_lower} for my {bp}?",
        "Please {syn_lower} for my {bp}",
        "I would like you to {syn_lower} for my {bp}"
    ]
    text = random.choice(templates).format(syn=syn, syn_lower=syn.lower(), bp=bp_variant)
    text = maybe_add_ending(text)
    text = maybe_append_noise(text)
    # For automatic massage, first detect the body part, then move, then start the massage.
    pipeline = [f"[x, y, z] = detect_body_part('{bp}')", "move_to([x, y, z])", f"automatic_massage('{bp}')"]
    return text, pipeline

# ------------------------------
# Generate a Command Sequence
# ------------------------------
def generate_command_sequence():
    """
    Randomly chooses between 1 and 3 commands from the available command generators.
    Returns a tuple of (instruction_text, pipeline_list).
    """
    # Decide the number of commands: 50% chance for 1, 30% for 2, 20% for 3.
    num_commands = random.choices([1, 2, 3], weights=[0.5, 0.3, 0.2])[0]
    command_texts = []
    pipeline = []
    # Choose random commands and accumulate their text and pipeline.
    for _ in range(num_commands):
        cmd_func = random.choice([
            cmd_start, cmd_stop, cmd_home, cmd_detect,
            cmd_move, cmd_change_force_relative, cmd_change_force_absolute, cmd_automatic_massage
        ])
        text, cmd_pipeline = cmd_func()
        command_texts.append(text)
        pipeline.extend(cmd_pipeline)
    # Join the command texts with a connector so the instruction reads naturally.
    instruction_text = "; then ".join(command_texts)
    return instruction_text, pipeline

# ------------------------------
# Dataset Generation
# ------------------------------
num_samples = 5000
dataset = []

instruction_prompt = (
    "You are provided with high-level instructions for operating a massage robot. "
    "Create an executable plan in Python that structures task execution through a sub-task pipeline. "
    "This pipeline should be composed exclusively of the functions listed below in the Capabilities section, "
    "arranged in a logical and correct order so that it can be directly executed. "
    "Your response should only consist of the pipeline without additional information.\n\n"
    "Capabilities:\n"
    "    start() → Initializes the robot.\n"
    "    stop() → Stops the robot.\n"
    "    home() → Moves the robot to the home position.\n"
    "    [x, y, z] = detect_body_part(part_name) → Detects the specified body part and returns the coordinates.\n"
    "    move_to([x, y, z]) → Moves the robot to the specified coordinates.\n"
    "    change_force(mode, value) → Adjusts the massage force based on the specified mode:\n"
    "        - If mode is 'absolute', then value is any real number, setting the force directly.\n"
    "        - If mode is 'relative', then value is between -1 and 1, modifying the current force F as:\n"
    "          F_new = (1 + value) * F\n"
    "    automatic_massage(part_name) → Automatically massages the specified body part.\n"
)

for _ in range(num_samples):
    input_text, pipeline_steps = generate_command_sequence()
    dataset.append({
        "instruction": instruction_prompt,
        "input": input_text,
        "response": pipeline_steps
    })

output_file = "massage_robot_dataset.json"
with open(output_file, "w") as f:
    json.dump(dataset, f, indent=4)

print(f"Dataset generated and saved to {output_file}")
