# Bone Camera Spawner for Blender
**This Blender add-on creates cameras targeting bones with advanced positioning options.**
Part of the *informatic flows* series by electro-cute-angels ❦
[![License](https://img.shields.io/npm/l/mithril.svg)](https://github.com/MithrilJS/mithril.js/blob/main/LICENSE) &nbsp;
[![Version](https://img.shields.io/badge/version-1.0-blue)](https://shields.io/) &nbsp;
![Static Badge](https://img.shields.io/badge/addon-blender-b?logo=addon&logoColor=%23ffff00&label=addon&color=ff00ff)
![screenshot-bone-camera-spawner-compressed](https://github.com/user-attachments/assets/placeholder-image-id)

## Features
- Create cameras targeting any bone in an armature
- Configure camera type (perspective or orthographic)
- Multiple positioning options:
  - First-person view attached to bones
  - Angled, perpendicular, or aligned to specific axes
  - Random positioning around bones
  - Custom fixed positions
- Easily switch between bone cameras in the viewport
- Automatically scales camera parameters based on bone size
- Creates organized camera collections in the scene

## Installation
1. Download `bone_camera_spawner.py` from this repository
2. Open Blender and go to Edit → Preferences → Add-ons
3. Click "Install..." and select the downloaded file
4. Enable the add-on by checking the box next to "Animation: Bone Camera Spawner"

## Usage
01. Select an armature in the 3D viewport
02. Open the sidebar panel (press N) and select the "Bone Cameras" tab
03. Configure camera settings:
   - Adjust camera distance, type, and lens parameters
   - Choose positioning method and options
   - Select bones to create cameras for
04. Click "Create Cameras" to generate cameras for each selected bone
05. Use the Camera Navigation section to switch between cameras

## Options Explained
### Camera Settings
- **Camera Distance**: Distance multiplier relative to bone length
- **Camera Type**: Choose between perspective or orthographic projection
- **Focal Length**: Lens size for perspective cameras (in mm)
- **Ortho Scale**: View size for orthographic cameras

### Camera Position
- **Bone Perspective**: First-person view from the bone's perspective
  - **Attach to**: Choose head (start), tail (end), or middle of bone
- **Position Type**: How to place the camera relative to the bone
  - **Angled**: Default position at an angle to the bone
  - **Random**: Random positioning around the bone
  - **Aligned**: Position along specific axes
  - **Perpendicular**: Position perpendicular to the bone direction
- **Align to**: When using aligned positioning, which axis to align to
- **Custom Position**: Specify a fixed position for all cameras

### Bone Selection
- Use the list to select which bones to create cameras for
- **Select All** / **Select None**: Quickly select or deselect all bones

## Camera Navigation
After creating cameras, they'll appear in the "Camera Navigation" section of the panel. Click on a bone name to:
- Set the camera as the active scene camera
- Switch the 3D view to that camera's perspective

## Troubleshooting
- If the panel doesn't appear, ensure an armature is selected in the viewport
- If cameras seem too close or too far from bones, adjust the Camera Distance value
- For small armatures, you might need to reduce the camera's clip start value
- For first-person views that appear flipped, try changing the attachment point

## Possible Use Cases / Workflows
- [Animation] Create dramatic camera angles for character animations
- [Rendering] Set up multiple camera views for batch rendering
- [Mocap] Visualize motion capture data from different perspectives
- [Rigging] Test bone constraints and IK chains from optimal viewpoints

## License
This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
---
electro-cute-angels ❦
