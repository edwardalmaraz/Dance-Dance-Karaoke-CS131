import os
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np

sr = 44100
OUTPUT_FILE = "voice_recording/output.wav"
_audio = None

def start_recording(max_seconds=300):
    global _audio
    os.makedirs("voice_recording", exist_ok=True)
    _audio = sd.rec(int(max_seconds * sr), samplerate=sr, channels=1, dtype=np.int16)

def stop_recording():
    global _audio
    sd.stop()
    if _audio is not None:
        wav.write(OUTPUT_FILE, sr, _audio)
        _audio = None
        print(f"Saved to {OUTPUT_FILE}")
