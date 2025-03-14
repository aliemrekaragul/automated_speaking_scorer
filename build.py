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

    # Create version info file
    version_info = '''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'Speaking Scorer'),
          StringStruct(u'FileDescription', u'Automated Speaking Performance Scorer'),
          StringStruct(u'FileVersion', u'1.0.0'),
          StringStruct(u'InternalName', u'speaking_scorer'),
          StringStruct(u'LegalCopyright', u'MIT License'),
          StringStruct(u'OriginalFilename', u'SpeakingScorer.exe'),
          StringStruct(u'ProductName', u'Speaking Scorer'),
          StringStruct(u'ProductVersion', u'1.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    version_file_path = os.path.join(workspace_dir, 'version_info.txt')
    with open(version_file_path, 'w') as f:
        f.write(version_info)

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
        '--add-data=prompts/*;prompts/',  # Include prompts directory
        '--clean',
        f'--version-file={version_file_path}',  # Add version info
        '--uac-admin',  # Request admin privileges
        '--noupx',  # Don't use UPX compression (reduces false positives)
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
    
    # Clean up version info file
    if os.path.exists(version_file_path):
        os.remove(version_file_path)
    
    print("\nBuild completed!")
    print(f"Executable and config file created in: {dist_path}")
    print("\nImportant Notes:")
    print("\n1. Remember to update the API keys in config.json before running the application.")
    print("\n2. If Windows Defender blocks the executable:")
    print("   - Right-click the file")
    print("   - Select 'Properties'")
    print("   - Check 'Unblock' in the security section")
    print("   - Click Apply and OK")
    print("\n3. You may need to run the executable as administrator the first time.")

if __name__ == '__main__':
    build_executable() 