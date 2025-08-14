# Survival Curves Extractor

A Python-based tool for extracting time-point data from survival curve images. This application provides an intuitive interface for digitizing survival curve plots and extracting precise time values at specific survival rate thresholds.

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[User Guide](USER_GUIDE.md)** - Comprehensive guide for non-technical users
- **[Visual Tutorial](VISUAL_TUTORIAL.md)** - Step-by-step with screenshots
- **[FAQ](FAQ.md)** - Common questions and troubleshooting
- **[Distribution Guide](DISTRIBUTION.md)** - How to build and distribute the app

## Features

- **Dataset Navigation**: Load and navigate through entire datasets of survival curve images
- **Axis Calibration**: Point-and-click calibration with zoom window for precision
- **Auto-Population**: Automatic creation of survival percentage guidelines (0%, 25%, 50%, 75%, 100%)
- **Status Tracking**: Mark images as Done/Error with visual indicators (✓/✗/○)
- **Progress Monitoring**: Real-time progress bar and completion statistics
- **Smart Filtering**: "Show only incomplete" option to focus on unfinished work
- **Auto-Save**: All changes saved automatically - no data loss
- **Enhanced Zoom**: Zoom window with survival percentage guidelines for precise clicking
- **Group Management**: Dynamic management of experimental groups from metadata
- **Cross-Platform**: Standalone executables for Windows and macOS

## 🚀 Download Ready-to-Use Application

### For Non-Technical Users
Download the pre-built application from the [Releases](https://github.com/NikitiusIv/survival_curves_extractor/releases) page:
- **Windows**: `SurvivalCurveExtractor-Windows-x64.zip`
- **macOS**: `SurvivalCurveExtractor-macOS-arm64.zip` (M1/M2) or `-x64.zip` (Intel)

See the [Quick Start Guide](QUICK_START.md) for installation instructions.

## 🛠️ Installation (For Developers)

### Requirements

- Python 3.9+
- Poetry (recommended) or pip

### Using Poetry

```bash
poetry install
```

### Using pip

```bash
pip install pillow
```

## Usage

### Running the Application

```bash
python main.py
```

### Workflow

1. **Load Dataset**: Click "Select Dataset" and choose your `extraction_data` folder
2. **Calibrate Axes**: 
   - Enter axis min/max values (e.g., X: 0-30, Y: 0-100)
   - Click "Start Calibration"
   - Click 4 points on the image following the prompts
3. **Extract Points**:
   - Survival lines appear automatically after calibration
   - Click where curves intersect the percentage lines
   - Points are auto-saved as you work
4. **Complete Image**: 
   - Click "Done" when finished
   - Use navigation arrows to move to next image
5. **Track Progress**: Monitor completion with progress bar and status indicators

### Key Features

- **Table-Based Selection**: All possible points are pre-populated; simply select and click
- **Inline Editing**: Double-click any time value to edit it directly
- **Keyboard Shortcuts**: Delete key to remove selected points
- **Auto-Cleanup**: Removing groups automatically cleans up associated data points
- **Visual Feedback**: Markers update in real-time as points are edited or moved

## Data Export Format

```json
{
  "metadata": {
    "x_axis_type": "time",
    "y_axis_type": "survival",
    "x_axis_units": "months",
    "y_axis_units": "% cumulative survival",
    "image_file": "plot_1.png",
    "extraction_date": "2024-01-15T10:30:00Z"
  },
  "data": {
    "0%": {"WT": 12.5, "KO": 10.2, "HT": 11.8},
    "25%": {"WT": 11.0, "KO": 8.5, "HT": 9.2},
    "50%": {"WT": 9.5, "KO": 7.0, "HT": 8.0},
    "75%": {"WT": 8.0, "KO": 5.5, "HT": 6.8},
    "100%": {"WT": 6.5, "KO": 4.0, "HT": 5.2}
  }
}
```

## Docker Support

Build and run using Docker:

```bash
docker build -t survival-curve-extractor .
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix survival-curve-extractor
```

## Development

- Built with Python and Tkinter for cross-platform compatibility
- Uses PIL/Pillow for image processing
- Poetry for dependency management
- Clean separation between UI and data processing logic

## License

This project is open source. Please see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.