import os
import soundfile as sf
import librosa
import numpy as np
from typing import List, Tuple

def read_file_as_bytes(file_path: str) -> bytes:
    """Read an audio file as bytes."""
    with open(file_path, "rb") as audio_file:
        return audio_file.read()

def get_audio_files(folder_path: str) -> List[str]:
    """Get all MP3 files from the specified folder."""
    audio_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.mp3'):
            audio_files.append(os.path.join(folder_path, file))
    return audio_files

def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
    """Load an audio file and return the audio data and sample rate."""
    try:
        audio_data, sample_rate = librosa.load(file_path, sr=None)
        return audio_data, sample_rate
    except Exception as e:
        raise ValueError(f"Error loading audio file {file_path}: {str(e)}")

def get_audio_duration(file_path: str) -> float:
    """Get the duration of an audio file in seconds."""
    try:
        audio_data, sample_rate = load_audio(file_path)
        return len(audio_data) / sample_rate
    except Exception as e:
        raise ValueError(f"Error getting audio duration for {file_path}: {str(e)}")

def validate_audio_file(file_path: str) -> bool:
    """Validate if the audio file is properly formatted and readable."""
    try:
        audio_data, sample_rate = load_audio(file_path)
        if len(audio_data) == 0:
            return False
        return True
    except Exception:
        return False 