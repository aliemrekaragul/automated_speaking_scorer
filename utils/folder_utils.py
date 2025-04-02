import os
from pathlib import Path
from pydub import AudioSegment
import shutil
import subprocess
import tempfile
import sys

def get_ffmpeg_path():
    """
    Get the path to the bundled ffmpeg binary.
    """
    if getattr(sys, 'frozen', False):
        # If the application is bundled (exe)
        base_path = sys._MEIPASS
    else:
        # If running in development
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if sys.platform == 'win32':
        ffmpeg_path = os.path.join(base_path, 'bin', 'ffmpeg.exe')
    else:
        ffmpeg_path = os.path.join(base_path, 'bin', 'ffmpeg')
    
    return ffmpeg_path

def sanitize_path(path: str) -> str:
    """
    Sanitize file path to handle non-ASCII characters.
    
    Args:
        path (str): Original file path
        
    Returns:
        str: Sanitized file path
    """
    return str(Path(path).resolve())

def convert_ogg_to_mp3(ogg_path: str, mp3_path: str) -> bool:
    """
    Convert an OGG file to MP3 format using ffmpeg directly if pydub fails.
    
    Args:
        ogg_path (str): Path to the source OGG file
        mp3_path (str): Path where the MP3 file should be saved
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        # Configure pydub to use bundled ffmpeg
        AudioSegment.converter = get_ffmpeg_path()
        
        # First try with pydub
        try:
            audio = AudioSegment.from_ogg(sanitize_path(ogg_path))
            audio.export(sanitize_path(mp3_path), format='mp3')
            return True
        except:
            # If pydub fails, try direct ffmpeg command
            try:
                # Create temporary directory for intermediate files
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Copy source file to temp directory with ASCII name
                    temp_ogg = os.path.join(temp_dir, "temp.ogg")
                    temp_mp3 = os.path.join(temp_dir, "temp.mp3")
                    shutil.copy2(ogg_path, temp_ogg)
                    
                    # Run ffmpeg command using bundled binary
                    cmd = [
                        get_ffmpeg_path(),
                        '-y',  # -y to overwrite output file
                        '-i', temp_ogg,  # input file
                        '-acodec', 'libmp3lame',  # use MP3 codec
                        '-ab', '192k',  # bitrate
                        temp_mp3  # output file
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    if result.returncode == 0 and os.path.exists(temp_mp3):
                        # Copy the converted file to final destination
                        shutil.copy2(temp_mp3, mp3_path)
                        return True
                    else:
                        print(f"FFmpeg conversion failed: {result.stderr}")
                        return False
                        
            except Exception as e:
                print(f"FFmpeg conversion failed: {str(e)}")
                return False
                
    except Exception as e:
        print(f"Error converting {ogg_path}: {str(e)}")
        return False

def process_student_folders(base_path: str) -> str:
    """
    Process all student folders, converting OGG files to MP3.
    
    Args:
        base_path (str): Base directory containing student folders
        
    Returns:
        str: Path to the mp3_files directory
    """
    # Create mp3_files directory if it doesn't exist
    mp3_dir = os.path.join(base_path, 'mp3_files')
    os.makedirs(mp3_dir, exist_ok=True)
    
    converted_count = 0
    failed_count = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(base_path):
        # Skip the mp3_files directory itself
        if 'mp3_files' in root:
            continue
            
        for file in files:
            if file.endswith('.ogg'):
                ogg_path = os.path.join(root, file)
                # Create a unique name for the MP3 file using the parent folder (student name)
                student_folder = Path(root).name
                mp3_filename = f"{student_folder}_{file[:-4]}.mp3"
                mp3_path = os.path.join(mp3_dir, mp3_filename)
                
                if convert_ogg_to_mp3(ogg_path, mp3_path):
                    converted_count += 1
                else:
                    failed_count += 1
    
    print(f"\nConversion Summary:")
    print(f"Successfully converted: {converted_count} files")
    print(f"Failed conversions: {failed_count} files")
    
    return mp3_dir
