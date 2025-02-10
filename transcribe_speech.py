#!/usr/bin/env python3
import argparse
import numpy as np
import speech_recognition as sr
import time
from faster_whisper import WhisperModel

def main():
    parser = argparse.ArgumentParser(
        description="Continuously record utterances and transcribe them, with optional hotwords from a file."
    )
    parser.add_argument("--model", default="medium",
                        choices=["tiny", "base", "small", "medium", "large-v1", "large-v2", "large-v3"],
                        help="Which Whisper model to use")
    parser.add_argument("--language", default="cs",
                        help="Language code for transcription (e.g., 'cs' for Czech, 'en' for English)")
    parser.add_argument("--energy_threshold", default=500, type=int,
                        help="Energy threshold for microphone input")
    parser.add_argument("--mic_duration_calib", default=2, type=float,
                        help="Duration (in seconds) for ambient noise calibration")
    parser.add_argument("--hotwords_file", default=None,
                        help="Path to a file containing hotwords (one per line) to bias the transcription")
    if sr.__version__:
        parser.add_argument("--default_microphone", default="",
                            help="(Optional) Name of the microphone to use on Linux (or leave blank for default)")
    args = parser.parse_args()

    hotwords_str = None
    if args.hotwords_file:
        try:
            with open(args.hotwords_file, "r", encoding="utf-8") as f:
                hotwords_list = [line.strip() for line in f if line.strip()]
            hotwords_str = ",".join(hotwords_list)
            print(f"Loaded hotwords: {hotwords_str}")
        except Exception as e:
            print(f"Error reading hotwords file: {e}")
            hotwords_str = None

    recognizer = sr.Recognizer() 
    recognizer.energy_threshold = args.energy_threshold
    recognizer.dynamic_energy_threshold = False
    recognizer.pause_threshold = 0.5  # Time after speech ends before recording stops TODO: 0.8 for slower speakers, might add an argument for this

    mic = sr.Microphone(device_index=1, sample_rate=16000)
    if args.default_microphone:
        for idx, name in enumerate(sr.Microphone.list_microphone_names()):
            if args.default_microphone.lower() in name.lower():
                mic = sr.Microphone(sample_rate=16000, device_index=idx)
                break

    if args.language.lower() == "en" and args.model != "large":
        model_name = f"{args.model}.en"
    else:
        model_name = args.model
    print(f"Loading faster-whisper model '{model_name}' ...")
    model = WhisperModel(model_name, download_root=f"C:/tmp/{model_name}", device="cuda")
    print("Model loaded.\n")
    
    print("Enter utterances continuously. After each utterance, the system will measure timing and transcribe the entire utterance.")
    print("Press Ctrl+C to exit.\n")
    
    try:
        while True:
            print("Listening for an utterance...")
            with mic:
                audio_data = recognizer.listen(mic)
            capture_end = time.time()  # Time when recording stopped
            
            raw_audio = audio_data.get_raw_data()
            np_audio = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32) / 32768.0
            
            print("Transcribing utterance...")
            segments, _ = model.transcribe(np_audio, language=args.language, hotwords=hotwords_str)
            transcribe_end = time.time()  # Time when transcription finished
            
            # Calculate transcription time from speech end to transcription end
            speech_end_time = capture_end - recognizer.pause_threshold
            transcription_time = (transcribe_end - speech_end_time) * 1000  # Convert to milliseconds
            
            transcription = " ".join(seg.text for seg in segments).strip()
            
            print("\n--- Utterance Transcription ---")
            print(transcription)
            print("--------------------------------")
            print(f"Transcription time (from speech end): {transcription_time:.2f} ms")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()