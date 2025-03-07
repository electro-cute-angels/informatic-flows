# Bone Animation Data Exporter for Blender
Part of the *informatic flows* series by electro-cute-angels ❦

This Blender add-on exports bone animation data to CSV format.

<img width="1512" alt="blender-electro-cute-screenshot" src="https://github.com/user-attachments/assets/a89dcfd0-3baa-49ef-86eb-0f47da0ad7b7" />

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

01. Select an armature in the 3D viewport
02. Go to File → Export → Bone Animation to CSV
03. Configure export options:
   - Choose which bone to export
   - Set frame range
   - Select coordinate system
   - Adjust precision and sampling rate
04. Click "Export" to save the CSV file

## Options Explained

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

## Troubleshooting

- If no bones appear in the dropdown, ensure your armature has bones and is properly rigged
- If the exported CSV contains unchanging values, check that your animation actually moves the selected bone
- Large files may take longer to process - use the Frame Step option to reduce file size

## Possible Use Cases

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

electro-cute-angels ❦
