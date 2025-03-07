# ✿˚* Bone Animation Data Exporter for Blender *˚☾

Part of the *informatic flows* series by electro-cute-angels❦

This Blender add-on exports bone animation data to CSV format for use with Pd-L2Ork or other applications.

## Features
- Export animation data from any bone in an armature
- Choose between normalized [-1, 1] values or world-space coordinates
- Select custom frame ranges and sampling rates
- Export single bones or all bones in an armature

## Installation
1. Download `bone_animation_exporter.py` from this repository
2. Open Blender and go to Edit → Preferences → Add-ons
3. Click "Install..." and select the downloaded file
4. Enable the add-on by checking the box next to "Import-Export: Animation to CSV Exporter"

## Usage
1. Select an armature in the 3D viewport
2. Go to File → Export → Bone Animation to CSV
3. Configure export options:
   - Choose which bone to export
   - Set frame range
   - Select coordinate system
   - Adjust precision and sampling rate
4. Click "Export" to save the CSV file

## Options Explained

### Bone Selection
- **Show Hidden Bones**: Include bones hidden in the viewport
- **Select Bone**: Choose a specific bone or "All Bones" to export

### Frame Range
- **Custom Frame Range**: Specify start and end frames
- Default uses the full animation range

### Coordinate System
- **Normalize to [-1, 1]**: Best for Pd-L2Ork integration
- **World Coordinates**: Raw position and rotation values

### Advanced Options
- **Frame Step**: Export every Nth frame
- **Decimal Precision**: Number of decimal places in values

## CSV Format

For a single bone export:
