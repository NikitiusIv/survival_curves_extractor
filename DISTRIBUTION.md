# Survival Curve Extractor - Distribution Guide

## Overview
This is a standalone application for extracting data points from survival curve images. The application is available for both Windows and macOS.

## Installation

### macOS
1. Download `SurvivalCurveExtractor-macOS-[arch].zip`
2. Extract the zip file
3. Double-click `SurvivalCurveExtractor.app` to run
4. If you see a security warning, right-click the app and select "Open"

### Windows
1. Download `SurvivalCurveExtractor-Windows-[arch].zip`
2. Extract the zip file
3. Double-click `SurvivalCurveExtractor.exe` to run
4. If Windows Defender shows a warning, click "More info" then "Run anyway"

## Features
- Load datasets of survival curve images
- Calibrate axes with precise zoom view
- Auto-populate survival percentage points
- Track progress with status indicators
- Export data to JSON format

## System Requirements
- **macOS**: 10.12 (Sierra) or later
- **Windows**: Windows 10 or later
- **Memory**: 4GB RAM minimum
- **Display**: 1280x800 minimum resolution

## Building from Source

If you want to build the application yourself:

### Prerequisites
- Python 3.9 or later (but less than 3.15)
- Poetry package manager

### Build Steps
1. Clone the repository
2. Install dependencies: `poetry install`
3. Run build script: `poetry run python build.py`
4. Find the executable in the `dist/` directory

### Alternative Build
For a simple single-file executable:
```bash
./build_simple.sh  # On macOS/Linux
# or
poetry run pyinstaller --onefile --windowed --name "SurvivalCurveExtractor" main.py
```

## Troubleshooting

### macOS Issues
- **"App is damaged"**: Run `xattr -cr SurvivalCurveExtractor.app` in Terminal
- **"Unidentified developer"**: Go to System Preferences > Security & Privacy and click "Open Anyway"

### Windows Issues
- **Missing DLL errors**: Install Visual C++ Redistributable
- **Antivirus warnings**: Add exception for the executable

## Support
For issues or questions, please visit: https://github.com/NikitiusIv/survival_curves_extractor