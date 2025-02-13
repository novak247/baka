import json
import random

# Function to generate random coordinates for move_to()
def random_coordinates():
    return [random.randint(-20, 20), random.randint(-20, 20), random.randint(-20, 20)]

# Function to generate random body parts
def random_body_part():
    return random.choice(["lower_back", "shoulders", "neck", "arms", "legs"])

# Define possible single-action inputs and their correct responses
single_action_entries = [
    ("Start the massage robot.", "start()"),
    ("Power on the system.", "start()"),
    ("Shut down the massage robot.", "stop()"),
    ("Turn off the system.", "stop()"),
    ("Return to the home position.", "home()"),
    ("Reset to the default position.", "home()"),
    (lambda: f"Detect my {random_body_part()}.", 
     lambda: f"[x, y, z] = detect_body_part('{random_body_part()}')"),
    (lambda: f"Move to position {random_coordinates()}.", 
     lambda: f"move_to({random_coordinates()})"),
    ("Reduce massage intensity by 40%.", "change_force('relative', -0.4)"),
    ("Increase the massage pressure by 20%.", "change_force('relative', 0.2)")
]

# Define valid multi-step sequences
multi_action_entries = [
    (lambda: f"Detect my {random_body_part()}, then move to that position.",
     lambda: [f"[x, y, z] = detect_body_part('{random_body_part()}')", "move_to([x, y, z])"]),
    
    (lambda: f"Move to position {random_coordinates()}, then reduce intensity by 30%.",
     lambda: [f"move_to({random_coordinates()})", "change_force('relative', -0.3)"]),
    
    ("Start the massage robot and move to home position.", ["start()", "home()"]),
    
    ("Return to home position, then shut down the system.", ["home()", "stop()"])
]

# Define valid three-step sequences
three_step_entries = [
    (lambda: f"Detect my {random_body_part()}, move to that position, then change force.",
     lambda: [f"[x, y, z] = detect_body_part('{random_body_part()}')",
              "move_to([x, y, z])",
              "change_force('relative', -0.3)"]),

    (lambda: f"Detect my {random_body_part()}, move to that position, then start automatic massage.",
     lambda: [f"[x, y, z] = detect_body_part('{random_body_part()}')",
              "move_to([x, y, z])",
              f"automatic_massage('{random_body_part()}')"])
]

# Generate dataset with exactly these input-response types
num_samples = 2000
dataset = []

for _ in range(num_samples):
    entry_type = random.choices(["single", "double", "triple"], weights=[0.5, 0.3, 0.2])[0]

    if entry_type == "single":
        input_text, response = random.choice(single_action_entries)
    elif entry_type == "double":
        input_text, response = random.choice(multi_action_entries)
    else:
        input_text, response = random.choice(three_step_entries)

    if callable(input_text):  # If input_text is a function, call it to get randomized values
        input_text = input_text()
    if callable(response):  # If response is a function, call it to get randomized values
        response = response()

    # Append structured entry
    dataset.append({
        "instruction": "You are provided with high-level instructions for operating a massage robot. "
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
                        "    automatic_massage(part_name) → Automatically massages the specified body part.\n",
        "input": input_text,
        "response": response
    })

# Save dataset to JSON file
output_file = "massage_robot_dataset.json"
with open(output_file, "w") as f:
    json.dump(dataset, f, indent=4)

print(f"Dataset generated and saved to {output_file}")
