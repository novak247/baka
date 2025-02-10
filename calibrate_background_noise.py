import speech_recognition as sr

recognizer = sr.Recognizer()

# Use your microphone as the source
with sr.Microphone(sample_rate=16000) as source:
    print("Calibrating ambient noise for 10 seconds (including robot noise)...")
    # This records 10 seconds and then sets the energy_threshold attribute.
    recognizer.adjust_for_ambient_noise(source, duration=10)
    print("Calibrated energy threshold:", recognizer.energy_threshold)

# Optionally, you can add a multiplier if you want to be even more conservative.
# For example, if the calibration sets energy_threshold to 1500, but you want to ignore
# noise that is slightly above that, you could do:
recognizer.energy_threshold *= 1.2  # Increase by 20%
print("Adjusted energy threshold:", recognizer.energy_threshold)
