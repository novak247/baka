#!/usr/bin/env python3
import argparse
import numpy as np
import speech_recognition as sr
import time
import webrtcvad  # pip install webrtcvad
from faster_whisper import WhisperModel

def is_speech_present(raw_audio, sample_rate=16000, frame_duration_ms=30, speech_ratio_threshold=0.5):
    """
    Returns True if the fraction of frames detected as speech is above the threshold.
    - raw_audio: bytes of 16-bit mono PCM data.
    - sample_rate: audio sample rate in Hz.
    - frame_duration_ms: duration of each frame in ms (typically 20-30 ms).
    - speech_ratio_threshold: minimum fraction of frames that must be speech.
    """
    vad = webrtcvad.Vad(2)  # mode 2: moderately aggressive
    frame_length = int(sample_rate * (frame_duration_ms / 1000.0) * 2)  # 2 bytes per sample (16-bit)
    frames = [
        raw_audio[i:i+frame_length]
        for i in range(0, len(raw_audio), frame_length)
        if len(raw_audio[i:i+frame_length]) == frame_length
    ]
    if not frames:
        return False

    speech_frames = sum(1 for frame in frames if vad.is_speech(frame, sample_rate))
    ratio = speech_frames / len(frames)
    return ratio >= speech_ratio_threshold

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
    # Default microphone prefix
    parser.add_argument("--default_microphone", default="Jabra Speak 710: USB Audio",
                        help="(Optional) Microphone name prefix to use on Linux. Leave empty to use system default.")
    args = parser.parse_args()

    # Load hotwords if provided
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
    recognizer.pause_threshold = 0.5  # seconds after speech ends before recording stops

    # Microphone selection based on name prefix
    mic = None
    mic_names = sr.Microphone.list_microphone_names()
    if args.default_microphone:
        selected_index = None
        for idx, name in enumerate(mic_names):
            if name.lower().startswith(args.default_microphone.lower()):
                selected_index = idx
                break
        if selected_index is not None:
            mic = sr.Microphone(sample_rate=16000, device_index=selected_index)
            print(f"Using microphone: {mic_names[selected_index]}")
        else:
            print("Warning: Specified microphone not found. Falling back to system default microphone.")
            mic = sr.Microphone(sample_rate=16000)
    else:
        mic = sr.Microphone(sample_rate=16000)
        default_name = mic_names[0] if mic_names else "Unknown"
        print(f"Using system default microphone: {default_name}")

    # Calibrate for ambient noise
    print(f"Calibrating microphone for ambient noise for {args.mic_duration_calib} seconds. Please remain silent...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=args.mic_duration_calib)
    print(f"Calibration complete. New energy threshold is: {recognizer.energy_threshold}\n")

    # Choose model name based on language and model selection
    if args.language.lower() == "en" and args.model != "large":
        model_name = f"{args.model}.en"
    else:
        model_name = args.model
    print(f"Loading faster-whisper model '{model_name}' ...")
    model = WhisperModel(model_name, download_root=f"/tmp/{model_name}", device="cuda")
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
            # Use VAD to filter out non-speech (random noise) segments
            if not is_speech_present(raw_audio):
                print("Detected noise without sufficient speech. Skipping transcription.\n")
                continue

            # Convert raw audio to normalized float32 array
            np_audio = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32) / 32768.0
            
            print("Transcribing utterance...")
            segments, _ = model.transcribe(np_audio, language=args.language, hotwords=hotwords_str)
            transcribe_end = time.time()  # Time when transcription finished
            
            # Calculate transcription time (from speech end)
            speech_end_time = capture_end - recognizer.pause_threshold
            transcription_time = (transcribe_end - speech_end_time) * 1000  # in ms
            
            transcription = " ".join(seg.text for seg in segments).strip()
            
            print("\n--- Utterance Transcription ---")
            print(transcription)
            print("--------------------------------")
            print(f"Transcription time (from speech end): {transcription_time:.2f} ms\n")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
