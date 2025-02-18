#!/usr/bin/env python3
import os
import json
import speech_recognition as sr
from vosk import Model, KaldiRecognizer

def main():
    # Path to the Czech VOSK model (vosk-model-small-cs-0.4-rhasspy)
    model_path = "model_cs"
    if not os.path.exists(model_path):
        print(f"Model not found at '{model_path}'. Please download and extract the Czech model from VOSK (vosk-model-small-cs-0.4-rhasspy).")
        return

    # Load the VOSK model
    print("Loading VOSK model...")
    model = Model(model_path)
    print("Model loaded successfully.")

    # Set up SpeechRecognition for automatic utterance segmentation.
    # The energy_threshold and pause_threshold values may need tuning depending on your environment.
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 500
    recognizer.dynamic_energy_threshold = False
    recognizer.pause_threshold = 0.8  # Adjust pause time (in seconds) to mark end-of-utterance

    # Use the default microphone with a 16kHz sample rate (required by the model)
    with sr.Microphone(device_index=1, sample_rate=16000) as source:
        
        # Continuously listen for utterances
        while True:
            try:
                print("\nListening for an utterance...")
                # 'listen' automatically stops recording after a pause
                audio_data = recognizer.listen(source)
                raw_audio = audio_data.get_raw_data()

                # Create a new VOSK recognizer instance for this utterance.
                vosk_recognizer = KaldiRecognizer(model, 16000)
                # Process the raw audio in chunks of 4000 bytes
                chunk_size = 4000
                for i in range(0, len(raw_audio), chunk_size):
                    chunk = raw_audio[i:i+chunk_size]
                    vosk_recognizer.AcceptWaveform(chunk)

                result_json = json.loads(vosk_recognizer.FinalResult())
                transcription = result_json.get("text", "")
                print("Transcription:", transcription)
            except Exception as e:
                print("Error during transcription:", e)

if __name__ == "__main__":
    main()
