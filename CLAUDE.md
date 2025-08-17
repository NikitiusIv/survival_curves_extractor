# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
```bash
python main.py
```

### Building the Application
```bash
# Using the build script (recommended)
poetry run python build.py

# Simple single-file executable
./build_simple.sh  # On macOS/Linux

# Manual PyInstaller build
poetry run pyinstaller --onefile --windowed --name "SurvivalCurveExtractor" main.py
```

### Managing Dependencies
```bash
# Install dependencies
poetry install

# Add a new dependency
poetry add <package_name>

# Update dependencies
poetry update
```

## High-Level Architecture

### Application Overview
The Survival Curve Extractor is a Python-based GUI application for digitizing survival curve plots from scientific papers. It uses Tkinter for the UI and PIL/Pillow for image processing.

### Core Components

1. **Main Application Class (`SurvivalCurveExtractor`)**: Located in `main.py`, this monolithic class manages the entire application state and UI. Key responsibilities:
   - Dataset navigation and image loading
   - Axis calibration system with 4-point clicking
   - Data point extraction with zoom view
   - Auto-save functionality with smart save logic
   - Progress tracking and status management

2. **Data Persistence Architecture**:
   - Uses JSON files for storing extracted data points
   - Implements a three-tier data priority system:
     1. User-entered results data (highest priority)
     2. Metadata from external sources
     3. Default/empty state
   - Includes flags to prevent save cascades during loading

3. **UI Layout**:
   - Left panel: Image canvas with calibration/extraction capabilities
   - Right panel: Control interface with axis configuration, group management, and data table
   - Navigation bar: Dataset selection and image navigation with progress tracking
   - Status indicators: Visual feedback (✓/✗/○) for completion status

4. **Key Technical Considerations**:
   - Cross-platform compatibility (Windows/macOS) with platform-specific UI adjustments
   - Custom button implementation for macOS due to Tkinter styling limitations
   - Zoom window functionality for precise point selection
   - Real-time marker updates as data is modified

### Data Flow
1. User selects dataset folder containing PNG images and optional metadata
2. Calibration establishes coordinate system mapping
3. Points are extracted by clicking on curve intersections
4. Data auto-saves to JSON files alongside images
5. Export format preserves metadata and extracted coordinates

### File Structure
- `extraction_data/`: Root dataset directory
  - `png/`: Image files to process
  - `metadata/`: Optional pre-populated metadata JSON files
  - `*_extracted_survival_time_points.json`: Output files with extracted data