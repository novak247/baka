#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import speech_recognition as sr

# Parameters
SAMPLE_RATE = 16000  # in Hz
RECORD_SECONDS = 2   # record for 2 seconds

# Create a recognizer and microphone instance
recognizer = sr.Recognizer()
mic = sr.Microphone(sample_rate=SAMPLE_RATE)

print("Recording knock for analysis... Please knock on your desk now!")
with mic as source:
    # You can adjust phrase_time_limit if needed
    audio_data = recognizer.listen(source, phrase_time_limit=RECORD_SECONDS)
print("Recording complete.")

# Convert the raw audio data to a NumPy array (assuming 16-bit PCM)
raw_audio = audio_data.get_raw_data()
audio_samples = np.frombuffer(raw_audio, dtype=np.int16)

# Perform the Fourier transform on the audio samples
fft_result = np.fft.rfft(audio_samples)
fft_freq = np.fft.rfftfreq(len(audio_samples), d=1/SAMPLE_RATE)
magnitude = np.abs(fft_result)

# Plot the frequency spectrum
plt.figure(figsize=(10, 6))
plt.plot(fft_freq, magnitude)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.title("Frequency Spectrum of the Knock")
plt.xlim(0, 4000)  # Limit x-axis to 0-4kHz (human speech and knocking usually fall within this range)
plt.grid(True)
plt.savefig("knock_spectrum.png", dpi=300, bbox_inches="tight")
plt.show()
