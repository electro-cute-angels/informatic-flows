# Bone Media Spawner for Blender
**This Blender add-on spawn images from bones with advanced positioning and tracking options.**
Part of the *informatic flows* series by electro-cute-angels ❦

[![License](https://img.shields.io/npm/l/mithril.svg)](https://github.com/MithrilJS/mithril.js/blob/main/LICENSE) &nbsp;
[![Version](https://img.shields.io/badge/version-1.0-blue)](https://shields.io/) &nbsp;
![Static Badge](https://img.shields.io/badge/addon-blender-b?logo=addon&logoColor=%23ffff00&label=addon&color=ff00ff)

## Features
- Attach images and videos to any bone in an armature
- Images/videos dynamically follow bones during animation
- Multiple positioning options:
  - Directly on the bone (zero distance)
  - Offset from the bone at a specified distance
  - Position relative to bone's head, tail, or center
  - Align along specific axes
- Media management options:
  - Select a folder containing images/videos
  - Randomly assign media to bones
  - Manually assign specific media to specific bones
- Auto-scaling based on bone size
- Fine-tuning with position and rotation offsets
- Easy cleanup with one-click removal of all media planes

## Installation
1. Download `bone_media_spawner.py` from this repository
2. Open Blender and go to Edit → Preferences → Add-ons
3. Click "Install..." and select the downloaded file
4. Enable the add-on by checking the box next to "Animation: Bone Media Spawner"

## Usage
01. Select an armature in the 3D viewport
02. Open the sidebar panel (press N) and select the "Bone Media" tab
03. Click "Select Media Folder" to choose a directory with images/videos
04. Configure media settings:
   - Set distance from bone and scale factor
   - Choose positioning method and options
   - Set any additional offsets and rotations
05. Select bones to attach media to
06. Assign media to bones (randomly or specifically)
07. Click "Create Media Planes" to generate media planes for each selected bone

## Options Explained
### Media Source
- **Media Directory**: Select a folder containing image and video files
- **Available Media Files**: List of all media files found in the selected directory
  - **Select All / Select None**: Quickly select or deselect all media files
  - **Random Assign**: Randomly assign available media to selected bones
  - **Assign Selected**: Assign selected media to selected bones

### Media Plane Settings
- **Distance from Bone**: How far to place the media from the bone (0 = directly on bone)
- **Scale Factor**: Size multiplier for the media plane relative to bone length
- **Position**: How to place the media relative to the bone
  - **Front**: In front of the bone
  - **Head**: At the head (start) of the bone
  - **Tail**: At the tail (end) of the bone
  - **Aligned**: Along specific axes
- **Align to**: When using aligned positioning, which axis to align to
- **Custom Position**: Specify a fixed position for all media
- **Position/Rotation Offset**: Fine adjustments to media placement and orientation

### Bone Selection
- Use the list to select which bones to create media for
- **Select All / Select None**: Quickly select or deselect all bones

## Media Assignment
You can assign media to bones in two ways:

1. **Random Assignment**: Select bones and click "Random Assign" to randomly assign available media
2. **Specific Assignment**: 
   - Select one or more bones
   - Select one or more media files
   - Click "Assign Selected"
   - If one media file is selected, it's assigned to all selected bones
   - If multiple media files are selected, they're assigned one-to-one with selected bones

## Supported File Formats
### Images
- JPG/JPEG, PNG, TIF/TIFF, BMP, TGA, EXR, HDR

### Videos
- MP4, MOV, AVI, MKV, WebM

## Troubleshooting
- If no media files appear in the list, make sure your folder contains supported file formats
- If media planes are too large or small, adjust the Scale Factor

## Possible Use Cases / Workflows
[..]

## License
This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
---
electro-cute-angels ❦
