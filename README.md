# Survival Curves Extractor

A Python-based tool for extracting time-point data from survival curve images. This application provides an intuitive interface for digitizing survival curve plots and extracting precise time values at specific survival rate thresholds.

## Features

- **Image Loading**: Load survival curve images from files or browse folders
- **Axis Calibration**: Point-and-click calibration for accurate coordinate mapping
- **Dynamic Group Management**: Add and manage experimental groups with scrollable interface
- **Interactive Point Selection**: Table-based point selection with click-to-set functionality
- **Real-time Editing**: Double-click to edit time values with automatic marker repositioning
- **Data Export**: Export extracted data to JSON format with metadata
- **Zoom Functionality**: Optional zoom window for precise point placement
- **Resizable Interface**: Draggable column borders for customizable workspace

## Installation

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

1. **Load Image**: Select a survival curve image file
2. **Calibrate Axes**: 
   - Click on X-axis minimum and maximum points
   - Enter corresponding values
   - Click on Y-axis minimum and maximum points
   - Enter corresponding values
3. **Set Groups**: Add experimental group names (WT, KO, HT, etc.)
4. **Extract Points**:
   - All possible group-survival rate combinations are auto-populated in the table
   - Select any row in the table
   - Click on the corresponding point in the image
   - Repeat for all desired points
5. **Export Data**: Save extracted time values to JSON format

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