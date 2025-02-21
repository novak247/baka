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
# Explicit Command Generator Functions
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
    return text, ["start()"]

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
    return text, ["stop()"]

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
    return text, ["home()"]

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
    return text, [f"[x, y, z] = detect_body_part('{bp}')"]

def cmd_move():
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
    return text, [f"change_force('relative', {value})"]

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
    return text, [f"change_force('absolute', {value:.2f})"]

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
    pipeline = [f"[x, y, z] = detect_body_part('{bp}')", "move_to([x, y, z])", f"automatic_massage('{bp}')"]
    return text, pipeline

# ------------------------------
# Ambiguous versions for latest turn (for applicable commands)
# ------------------------------
def ambiguous_change_force_relative():
    # Either produce a prefixed ambiguous command or a standalone word.
    if random.random() < 0.5:
        percentage = random.randint(10, 50)
        if random.random() < 0.5:
            verb = "reduce"
        else:
            verb = "increase"
        noun = random.choice(force_nouns)
        templates = [
            "Then {} {} by {}%",
            "After that, {} {} by {}%",
            "Also, {} {} by {}%"
        ]
        text = maybe_add_ending(randomize_case(random.choice(templates)).format(verb, noun, percentage))
        value = percentage / 100.0 if verb == "increase" else -percentage / 100.0
    else:
        # Standalone version: just a single word.
        if random.random() < 0.5:
            word = random.choice(increase_synonyms)
            value = 0.20  # default value
        else:
            word = random.choice(decrease_synonyms)
            value = -0.20
        text = maybe_add_ending(word.lower())
    pipeline = f"change_force('relative', {value})"
    return text, pipeline

def ambiguous_automatic_massage():
    # Either produce a prefixed version or a standalone version.
    if random.random() < 0.5:
        options = ["shoulders", "arms", "neck", "chest", "stomach", "hips", "knees", "elbows", "wrists"]
        bp = random.choice(options)
        templates = [
            "Then {}",
            "After that, {}",
            "Also {}",
            "Next {}",
            "And {}"
        ]
        text = maybe_add_ending(randomize_case(random.choice(templates)).format(bp))
    else:
        # Standalone version: just the body part name.
        options = ["shoulders", "arms", "neck", "chest", "stomach", "hips", "knees", "elbows", "wrists"]
        bp = random.choice(options)
        text = maybe_add_ending(randomize_case(bp))
    pipeline = "[x, y, z] = detect_body_part('{}')\nmove_to([x, y, z])\nautomatic_massage('{}')".format(bp, bp)
    return text, pipeline

# ------------------------------
# Map command types to their generators.
# Each entry: (explicit_function, ambiguous_function)
# For commands without an ambiguous version, ambiguous_function is None.
# ------------------------------
command_generators = {
    "start": (cmd_start, None),
    "stop": (cmd_stop, None),
    "home": (cmd_home, None),
    "detect": (cmd_detect, None),
    "move": (cmd_move, None),
    "change_force_relative": (cmd_change_force_relative, ambiguous_change_force_relative),
    "change_force_absolute": (cmd_change_force_absolute, None),
    "automatic_massage": (cmd_automatic_massage, ambiguous_automatic_massage)
}

# ------------------------------
# Generate a full explicit turn for conversation history.
# ------------------------------
def generate_explicit_turn():
    cmd_type = random.choice(list(command_generators.keys()))
    explicit_fn, _ = command_generators[cmd_type]
    text, pipeline = explicit_fn()
    return "User: " + text + "\nAssistant: " + "\n".join(pipeline)

# ------------------------------
# Generate the latest user turn.
# Instead of a single command, this function now generates a sequence of commands.
# Each command is generated from a random command type, using ambiguous generators when possible (if context exists),
# or falling back to the explicit generator.
# ------------------------------
def generate_latest_turn(has_history):
    # Choose a random number of commands (1 to 5) for the latest turn.
    num_cmds = random.choices([1, 2, 3, 4, 5], weights=[0.2, 0.25, 0.25, 0.15, 0.15])[0]
    texts = []
    pipeline_cmds = []
    for _ in range(num_cmds):
        cmd_type = random.choice(list(command_generators.keys()))
        explicit_fn, ambiguous_fn = command_generators[cmd_type]
        if has_history and ambiguous_fn is not None:
            t, p = ambiguous_fn()
        else:
            t, p = explicit_fn()
            if t.startswith("User: "):
                t = t[len("User: "):]
        texts.append(t)
        if isinstance(p, list):
            pipeline_cmds.append("\n".join(p))
        else:
            pipeline_cmds.append(p)
    latest_text = "; ".join(texts)
    expected_response = "\n".join(pipeline_cmds)
    return latest_text, expected_response

# ------------------------------
# Generate one conversation entry.
# ------------------------------
def generate_conversation_entry():
    """
    With 50% chance, include conversation history (1-3 explicit turns);
    then generate the latest user input (which may consist of multiple commands).
    Returns:
      conversation_history (string), latest_user_input (string), expected_response (string)
    """
    has_history = random.random() < 0.5
    if has_history:
        num_turns = random.randint(1, 3)
        full_turns = [generate_explicit_turn() for _ in range(num_turns)]
        conversation_history = "\n".join(full_turns)
    else:
        conversation_history = ""
    
    latest_input, expected_response = generate_latest_turn(has_history)
    return conversation_history, latest_input, expected_response

# ------------------------------
# Prompt Template (exactly as specified)
# ------------------------------
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

# ------------------------------
# Generate dataset and save to JSON
# ------------------------------
num_samples = 5000
dataset = []

for _ in range(num_samples):
    conv_history, latest_input, response = generate_conversation_entry()
    dataset.append({
        "instruction": train_prompt_style_context,
        "conversation_history": conv_history,
        "latest_user_input": latest_input,
        "response": response
    })

output_file = "massage_robot_dataset_with_mixed_commands.json"
with open(output_file, "w") as f:
    json.dump(dataset, f, indent=4)

print(f"Dataset generated and saved to {output_file}")
