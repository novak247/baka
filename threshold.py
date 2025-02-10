#!/usr/bin/env python3
import pyaudio
import audioop
import time

def record_energy(duration=10, chunk_size=1024, sample_rate=16000):
    """
    Records audio for the specified duration (in seconds) and calculates the RMS energy
    for each audio chunk. Returns a list of RMS values.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk_size)
    
    print(f"Recording for {duration} seconds to calculate energy...")
    rms_values = []
    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            data = stream.read(chunk_size, exception_on_overflow=False)
        except Exception as e:
            print("Error reading audio:", e)
            continue
        
        # Compute RMS energy: 2 bytes per sample for 16-bit audio.
        rms = audioop.rms(data, 2)
        rms_values.append(rms)
        print(f"RMS: {rms}")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    return rms_values

def main():
    duration = 10  # seconds to record for calibration
    rms_values = record_energy(duration=duration)
    
    if rms_values:
        avg_rms = sum(rms_values) / len(rms_values)
        min_rms = min(rms_values)
        max_rms = max(rms_values)
        print("\n--- Energy Statistics ---")
        print(f"Average RMS: {avg_rms:.2f}")
        print(f"Minimum RMS: {min_rms}")
        print(f"Maximum RMS: {max_rms}")
        print("-------------------------")
    else:
        print("No RMS values were recorded.")

if __name__ == "__main__":
    main()
