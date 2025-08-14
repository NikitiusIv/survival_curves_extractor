#!/usr/bin/env python3
"""
Build script for creating standalone executables of Survival Curve Extractor
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean .spec file if it exists
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        if spec_file.name != 'survival_curve_extractor.spec':
            print(f"Removing {spec_file}...")
            spec_file.unlink()

def build_executable():
    """Build the executable using PyInstaller"""
    system = platform.system()
    print(f"Building for {system}...")
    
    # Use poetry run to ensure we're using the right environment
    cmd = [
        'poetry', 'run', 'pyinstaller',
        '--clean',
        '--noconfirm',
        'survival_curve_extractor.spec'
    ]
    
    print("Running:", ' '.join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error building executable:")
        print(result.stderr)
        return False
    
    print("Build successful!")
    return True

def create_distribution():
    """Create a distribution package"""
    system = platform.system()
    dist_dir = Path('dist')
    
    if system == 'Darwin':  # macOS
        app_path = dist_dir / 'SurvivalCurveExtractor.app'
        if app_path.exists():
            # Create a DMG file (optional, requires additional tools)
            print(f"Application bundle created at: {app_path}")
            
            # Create a simple zip file for distribution
            zip_name = f'SurvivalCurveExtractor-macOS-{platform.machine()}.zip'
            print(f"Creating {zip_name}...")
            subprocess.run(['zip', '-r', zip_name, 'SurvivalCurveExtractor.app'], 
                         cwd=dist_dir, check=True)
            print(f"Distribution package created: dist/{zip_name}")
    
    elif system == 'Windows':
        exe_path = dist_dir / 'SurvivalCurveExtractor.exe'
        if exe_path.exists():
            print(f"Executable created at: {exe_path}")
            
            # Create a zip file for distribution
            zip_name = f'SurvivalCurveExtractor-Windows-{platform.machine()}.zip'
            print(f"Creating {zip_name}...")
            
            # On Windows, we might not have zip command, use Python's zipfile
            import zipfile
            with zipfile.ZipFile(dist_dir / zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(exe_path, 'SurvivalCurveExtractor.exe')
            
            print(f"Distribution package created: dist/{zip_name}")
    
    else:  # Linux
        exe_path = dist_dir / 'SurvivalCurveExtractor'
        if exe_path.exists():
            print(f"Executable created at: {exe_path}")
            
            # Create a tar.gz file for distribution
            tar_name = f'SurvivalCurveExtractor-Linux-{platform.machine()}.tar.gz'
            print(f"Creating {tar_name}...")
            subprocess.run(['tar', '-czf', tar_name, 'SurvivalCurveExtractor'], 
                         cwd=dist_dir, check=True)
            print(f"Distribution package created: dist/{tar_name}")

def main():
    print("Survival Curve Extractor Build Script")
    print("=" * 50)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build the executable
    if build_executable():
        # Create distribution package
        create_distribution()
        
        print("\nBuild completed successfully!")
        print("\nTo run the application:")
        
        system = platform.system()
        if system == 'Darwin':
            print("  - Double-click dist/SurvivalCurveExtractor.app")
            print("  - Or run: open dist/SurvivalCurveExtractor.app")
        elif system == 'Windows':
            print("  - Double-click dist/SurvivalCurveExtractor.exe")
        else:
            print("  - Run: ./dist/SurvivalCurveExtractor")
    else:
        print("\nBuild failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()