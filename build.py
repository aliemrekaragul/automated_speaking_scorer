import PyInstaller.__main__
import os
import sys

def build_executable():
    # Get the absolute path to the workspace directory
    workspace_dir = os.path.abspath(os.path.dirname(__file__))
    
    dist_path = os.path.join(workspace_dir, 'dist')
    build_path = os.path.join(workspace_dir, 'build')
    icon_path = os.path.join(workspace_dir, 'resources', 'app_icon.ico')
    
    os.makedirs(dist_path, exist_ok=True)
    os.makedirs(build_path, exist_ok=True)

    # PyInstaller arguments
    args = [
        'main.py',  
        '--name=SpeakingScorer',  # Name of the executable
        '--onefile',  # Create a single executable file
        '--windowed',  # Don't show console window on Windows
        f'--distpath={dist_path}',
        f'--workpath={build_path}',
        '--hidden-import=google.cloud.aiplatform',
        '--hidden-import=soundfile',
        '--hidden-import=librosa',
        '--hidden-import=numpy',
        '--hidden-import=pandas',
        '--hidden-import=xlsxwriter',
        '--hidden-import=PyQt6',
        '--hidden-import=json',
        '--add-data=task_definitions.py;.',
        '--add-data=utils/config_manager.py;utils',
        '--clean',
    ]

    if sys.platform.startswith('win') and os.path.exists(icon_path):
        args.extend([
            f'--icon={icon_path}',
        ])
    elif sys.platform.startswith('darwin') and os.path.exists(icon_path.replace('.ico', '.icns')):
        args.extend([
            f'--icon={icon_path.replace(".ico", ".icns")}',
        ])

    PyInstaller.__main__.run(args)
    
    print("\nBuild completed!")
    print(f"Executable and config file created in: {dist_path}")
    print("Remember to update the API keys in config.json before running the application.")

if __name__ == '__main__':
    build_executable() 