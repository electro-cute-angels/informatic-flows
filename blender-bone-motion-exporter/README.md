# Bone Motion Exporter for Blender
**This Blender add-on exports bone motion data to CSV and JSON formats.**
Part of the *informatic flows* series by electro-cute-angels ❦
[![License](https://img.shields.io/npm/l/mithril.svg)](https://github.com/MithrilJS/mithril.js/blob/main/LICENSE) &nbsp;
[![Version](https://img.shields.io/badge/version-1.1-blue)](https://shields.io/) &nbsp;
![Static Badge](https://img.shields.io/badge/addon-blender-b?logo=addon&logoColor=%23ffff00&label=addon&color=ff00ff)
![screenshot-motion-data-exporter-compressed](https://github.com/user-attachments/assets/c400df5c-8929-4fb9-941c-5769040591dd)

## Features
- Export motion data from any bone in an armature
- **New in v1.1**: Export to CSV or JSON format with automatic file extension updates
- Choose between normalized [-1, 1] values or world-space coordinates
- Select custom frame ranges and sampling rates
- Export single bones or all bones in an armature
- Intelligent JSON organization by frame and bone type

## Installation
1. Download `bone_motion_exporter.py` from this repository
2. Open Blender and go to Edit → Preferences → Add-ons
3. Click "Install..." and select the downloaded file
4. Enable the add-on by checking the box next to "Import-Export: Bone Motion Data Exporter"

## Usage
01. Select an armature in the 3D viewport
02. Go to File → Export → Bone Motion Data
03. Configure export options:
   - Select export format (CSV or JSON)
   - Choose which bone to export
   - Set frame range
   - Select coordinate system
   - Adjust precision and sampling rate
04. Click "Export" to save the file (extension updates automatically based on format)

## Options Explained
### Export Format
- **CSV**: Comma-separated values format (best for spreadsheets)
- **JSON**: JavaScript Object Notation format (best for web applications and advanced processing)

### Bone Selection
- **Show Hidden Bones**: Include bones hidden in the viewport
- **Select Bone**: Choose a specific bone or "All Bones" to export

### Frame Range
- **Custom Frame Range**: Specify start and end frames
- Default uses the full animation range

### Coordinate System
- **Normalize to [-1, 1]**: Best for further processing
- **World Coordinates**: Raw position and rotation values

### Advanced Options
- **Frame Step**: Export every Nth frame
- **Decimal Precision**: Number of decimal places in values

## CSV Format
For a single bone export:
| frame | pos_x     | pos_y     | pos_z      | rot_x     | rot_y     | rot_z     |
|-------|-----------|-----------|------------|-----------|-----------|-----------|
| 1     | 0.000000  | 0.000000  | 0.000000   | 0.000000  | 0.000000  | 0.000000  |
| 2     | 0.125631  | 0.098452  | -0.045812  | 0.023599  | 0.000000  | 0.001571  |
| 3     | 0.261242  | 0.196904  | -0.091623  | 0.047198  | 0.003142  | 0.003142  |
| ...   | ...       | ...       | ...        | ...       | ...       | ...       |

For multiple bones export:
| frame | Hips_pos_x | Hips_pos_y | Hips_pos_z | Hips_rot_x | Hips_rot_y | Hips_rot_z | Spine_pos_x | ... |
|-------|------------|------------|------------|------------|------------|------------|-------------|-----|
| 1     | 0.000000   | 0.000000   | 0.000000   | 0.000000   | 0.000000   | 0.000000   | 0.000000    | ... |
| 2     | 0.125631   | 0.098452   | -0.045812  | 0.023599   | 0.000000   | 0.001571   | 0.129842    | ... |
| ...   | ...        | ...        | ...        | ...        | ...        | ...        | ...         | ... |

## JSON Format (New in v1.1)
The JSON export organizes data in a structured format with three main sections:

### 1. Metadata
```json
"metadata": {
  "format": "bone motion data by frame and by bone type",
  "coordinate_system": "normalized",
  "frame_count": 250,
  "bone_count": 32,
  "frame_range": [1, 250]
}
```

### 2. By Frame
Data organized chronologically, with each frame containing all bone positions/rotations:
```json
"by_frame": {
  "1": {
    "Hips": {
      "position": {"x": 0.0, "y": 0.0, "z": 0.0},
      "rotation": {"x": 0.0, "y": 0.0, "z": 0.0}
    },
    "Spine": {
      "position": {"x": 0.1, "y": 0.2, "z": 0.3},
      "rotation": {"x": 0.01, "y": 0.02, "z": 0.03}
    }
  },
  "2": { /* frame 2 data */ }
}
```

### 3. By Bone Type
Data organized by anatomical region, making it easy to work with related bones:
```json
"by_bone_type": {
  "arm": {
    "LeftArm": {
      "frames": {
        "1": { /* position and rotation */ },
        "2": { /* position and rotation */ }
      }
    },
    "RightArm": { /* similar structure */ }
  },
  "leg": { /* leg bones */ },
  "spine": { /* spine bones */ },
  "head": { /* head bones */ },
  "hip": { /* hip bones */ },
  "other": { /* uncategorized bones */ }
}
```

## Troubleshooting
- If no bones appear in the dropdown, ensure your armature has bones and is properly rigged
- If the exported file contains unchanging values, check that your animation actually moves the selected bone
- Large files may take longer to process - use the Frame Step option to reduce file size

## Possible Use Cases / Workflows
- Generative music in Pure Data
- Web-based animations
- ML model training
- .. more use cases soon

## License
This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
---
electro-cute-angels ❦
