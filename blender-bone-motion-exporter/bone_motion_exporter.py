bl_info = {
    "name": "Bone Motion Data Exporter",
    "author": "electro-cute-angels",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "File > Export > Bone Motion Data",
    "description": "Export bone motion data to CSV/JSON - part of 'informatic flows' series",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

import bpy
import csv
import json
import os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty, FloatProperty
from bpy.types import Operator, Panel

def get_bones_callback(self, context):
    items = []
    
    obj = context.active_object
    if obj and obj.type == 'ARMATURE' and obj.pose:
        for i, bone in enumerate(obj.pose.bones):
            if not self.show_hidden_bones and bone.bone.hide:
                continue
                
            items.append((
                bone.name,
                bone.name,
                f"Export motion from bone: {bone.name}"
            ))
    
    items.insert(0, ("ALL", "All Bones", "Export motion from all bones (will create a wider data structure)"))
    
    if len(items) == 1:
        items.append(("NONE", "No Bones Found", "No bones found in the active armature"))
    
    return items

def get_animation_range(context):
    obj = context.active_object
    if obj and obj.animation_data and obj.animation_data.action:
        frame_range = obj.animation_data.action.frame_range
        return (int(frame_range[0]), int(frame_range[1]))
    return (1, 250)

class BONE_OT_export_motion_data(Operator, ExportHelper):
    bl_idname = "export.bone_motion_data"
    bl_label = "Export Bone Motion Data"
    
    filename_ext = StringProperty(
        default=".csv",
        options={'HIDDEN'}
    )
    
    filter_glob: StringProperty(
        default="*.csv;*.json",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    export_format: EnumProperty(
        name="Format",
        description="Choose the export format",
        items=(
            ('CSV', "CSV", "Comma-separated values format"),
            ('JSON', "JSON", "JavaScript Object Notation format")
        ),
        default='CSV'
    )
    
    show_hidden_bones: BoolProperty(
        name="Show Hidden Bones",
        description="Include bones that are hidden in the viewport",
        default=False
    )
    
    bone_to_export: EnumProperty(
        name="Select Bone",
        description="Choose which bone's motion to export",
        items=get_bones_callback
    )
    
    use_custom_range: BoolProperty(
        name="Custom Frame Range",
        description="Use custom start and end frames instead of the full animation",
        default=False
    )
    
    start_frame: IntProperty(
        name="Start Frame",
        description="First frame to export",
        default=1,
        min=1
    )
    
    end_frame: IntProperty(
        name="End Frame",
        description="Last frame to export",
        default=250,
        min=1
    )
    
    sample_all_frames: BoolProperty(
        name="Export All Frames",
        description="Export every single frame (may result in large files)",
        default=False
    )
    
    coordinate_system: EnumProperty(
        name="Coordinate System",
        description="Choose the coordinate system for export",
        items=(
            ('NORMALIZED', "Normalize to [-1, 1]", "Normalize values to range [-1, 1] for Pd-L2Ork"),
            ('WORLD', "World Coordinates", "Export raw world space coordinates"),
        ),
        default='NORMALIZED'
    )
    
    frame_step: IntProperty(
        name="Frame Step",
        description="Export every Nth frame (1 = all frames)",
        default=1,
        min=1
    )
    
    precision: IntProperty(
        name="Decimal Precision",
        description="Number of decimal places in exported values",
        default=6,
        min=1,
        max=10
    )
    
    def invoke(self, context, event):
        self.update_extension(context)
        
        start, end = get_animation_range(context)
        self.start_frame = start
        self.end_frame = end
        return super().invoke(context, event)
    
    def update_extension(self, context):
        if self.export_format == 'CSV':
            self.filename_ext = ".csv"
        elif self.export_format == 'JSON':
            self.filename_ext = ".json"
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Bone Motion Exporter ❦")
        
        box = layout.box()
        box.label(text="Export Format:")
        box.prop(self, "export_format", expand=True)
        
        box = layout.box()
        box.label(text="Bone Selection:")
        box.prop(self, "show_hidden_bones")
        box.prop(self, "bone_to_export")
        
        if self.bone_to_export == "ALL":
            box.label(text="Note: Exporting all bones will create a wider data structure", icon='INFO')
        
        box = layout.box()
        box.label(text="Frame Range:")
        box.prop(self, "use_custom_range")
        sub = box.column()
        sub.enabled = self.use_custom_range
        sub.prop(self, "start_frame")
        sub.prop(self, "end_frame")
        
        box = layout.box()
        box.label(text="Export Options:")
        box.prop(self, "sample_all_frames")
        
        box.label(text="Coordinate System:")
        box.prop(self, "coordinate_system", expand=True)
        
        box = layout.box()
        row = box.row()
        row.prop(self, "frame_step")
        row.prop(self, "precision")
    
    def execute(self, context):
        self.update_extension(context)
        
        filepath = self.filepath
        if not filepath.endswith(self.filename_ext):
            filepath += self.filename_ext
        
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object must be an armature")
            return {'CANCELLED'}
        
        if not obj.animation_data or not obj.animation_data.action:
            self.report({'ERROR'}, f"No motion data found on armature {obj.name}")
            return {'CANCELLED'}
        
        pose_bones = obj.pose.bones
        bones_to_export = []
        
        if self.bone_to_export == "ALL":
            for bone in pose_bones:
                if not self.show_hidden_bones and bone.bone.hide:
                    continue
                bones_to_export.append(bone)
        else:
            if self.bone_to_export in pose_bones:
                bones_to_export = [pose_bones[self.bone_to_export]]
            else:
                self.report({'ERROR'}, f"Selected bone '{self.bone_to_export}' not found")
                return {'CANCELLED'}
        
        if not bones_to_export:
            self.report({'ERROR'}, "No bones found to export")
            return {'CANCELLED'}
        
        if self.use_custom_range:
            start_frame = self.start_frame
            end_frame = self.end_frame
        else:
            action = obj.animation_data.action
            frame_range = action.frame_range
            start_frame = int(frame_range[0])
            end_frame = int(frame_range[1])
        
        if start_frame > end_frame:
            self.report({'ERROR'}, "Start frame must be less than or equal to end frame")
            return {'CANCELLED'}
        
        original_frame = context.scene.frame_current
        
        if self.sample_all_frames:
            sample_interval = self.frame_step
        else:
            sample_interval = max(self.frame_step, (end_frame - start_frame) // 500)
        
        frames_to_sample = range(start_frame, end_frame + 1, sample_interval)
        
        bone_data = {}
        
        if self.coordinate_system == 'NORMALIZED':
            for bone in bones_to_export:
                positions = []
                rotations = []
                
                sample_steps = max(1, len(frames_to_sample) // 20)
                for frame_idx, frame in enumerate(frames_to_sample):
                    if frame_idx % sample_steps != 0 and frame != frames_to_sample[-1]:
                        continue
                    
                    context.scene.frame_set(frame)
                    context.view_layer.update()
                    
                    bone_matrix = obj.matrix_world @ bone.matrix
                    
                    loc = bone_matrix.to_translation()
                    positions.append([loc.x, loc.y, loc.z])
                    
                    rot = bone_matrix.to_euler()
                    rotations.append([rot.x, rot.y, rot.z])
                
                min_pos = [min(p[i] for p in positions) for i in range(3)]
                max_pos = [max(p[i] for p in positions) for i in range(3)]
                min_rot = [min(r[i] for r in rotations) for i in range(3)]
                max_rot = [max(r[i] for r in rotations) for i in range(3)]
                
                for i in range(3):
                    if min_pos[i] == max_pos[i]:
                        min_pos[i] -= 0.001
                        max_pos[i] += 0.001
                    if min_rot[i] == max_rot[i]:
                        min_rot[i] -= 0.001
                        max_rot[i] += 0.001
                
                bone_data[bone.name] = {
                    'min_pos': min_pos,
                    'max_pos': max_pos,
                    'min_rot': min_rot,
                    'max_rot': max_rot
                }
        
        try:
            animation_data = []
            frames_data = {}
            
            for frame in frames_to_sample:
                context.scene.frame_set(frame)
                context.view_layer.update()
                
                frame_data = {"frame": frame}
                frame_bones_data = {}
                
                for bone in bones_to_export:
                    bone_matrix = obj.matrix_world @ bone.matrix
                    
                    loc = bone_matrix.to_translation()
                    rot = bone_matrix.to_euler()
                    
                    if self.coordinate_system == 'WORLD':
                        bone_values = {
                            "position": {
                                "x": round(loc.x, self.precision),
                                "y": round(loc.y, self.precision),
                                "z": round(loc.z, self.precision)
                            },
                            "rotation": {
                                "x": round(rot.x, self.precision),
                                "y": round(rot.y, self.precision),
                                "z": round(rot.z, self.precision)
                            }
                        }
                    else:  # NORMALIZED
                        min_pos = bone_data[bone.name]['min_pos']
                        max_pos = bone_data[bone.name]['max_pos']
                        min_rot = bone_data[bone.name]['min_rot']
                        max_rot = bone_data[bone.name]['max_rot']
                        
                        norm_pos = [
                            2.0 * (loc.x - min_pos[0]) / (max_pos[0] - min_pos[0]) - 1.0,
                            2.0 * (loc.y - min_pos[1]) / (max_pos[1] - min_pos[1]) - 1.0,
                            2.0 * (loc.z - min_pos[2]) / (max_pos[2] - min_pos[2]) - 1.0
                        ]
                        
                        norm_rot = [
                            2.0 * (rot.x - min_rot[0]) / (max_rot[0] - min_rot[0]) - 1.0,
                            2.0 * (rot.y - min_rot[1]) / (max_rot[1] - min_rot[1]) - 1.0,
                            2.0 * (rot.z - min_rot[2]) / (max_rot[2] - min_rot[2]) - 1.0
                        ]
                        
                        norm_pos = [max(-1.0, min(1.0, v)) for v in norm_pos]
                        norm_rot = [max(-1.0, min(1.0, v)) for v in norm_rot]
                        
                        bone_values = {
                            "position": {
                                "x": round(norm_pos[0], self.precision),
                                "y": round(norm_pos[1], self.precision),
                                "z": round(norm_pos[2], self.precision)
                            },
                            "rotation": {
                                "x": round(norm_rot[0], self.precision),
                                "y": round(norm_rot[1], self.precision),
                                "z": round(norm_rot[2], self.precision)
                            }
                        }
                    
                    if self.export_format == 'CSV':
                        if len(bones_to_export) == 1:
                            frame_data["pos_x"] = bone_values["position"]["x"]
                            frame_data["pos_y"] = bone_values["position"]["y"]
                            frame_data["pos_z"] = bone_values["position"]["z"]
                            frame_data["rot_x"] = bone_values["rotation"]["x"]
                            frame_data["rot_y"] = bone_values["rotation"]["y"]
                            frame_data["rot_z"] = bone_values["rotation"]["z"]
                        else:
                            frame_data[f"{bone.name}_pos_x"] = bone_values["position"]["x"]
                            frame_data[f"{bone.name}_pos_y"] = bone_values["position"]["y"]
                            frame_data[f"{bone.name}_pos_z"] = bone_values["position"]["z"]
                            frame_data[f"{bone.name}_rot_x"] = bone_values["rotation"]["x"]
                            frame_data[f"{bone.name}_rot_y"] = bone_values["rotation"]["y"]
                            frame_data[f"{bone.name}_rot_z"] = bone_values["rotation"]["z"]
                    
                    frame_bones_data[bone.name] = bone_values
                
                if self.export_format == 'JSON':
                    frames_data[str(frame)] = frame_bones_data
                else:  
                    animation_data.append(frame_data)
            
            if self.export_format == 'CSV':
                self.export_csv(filepath, animation_data)
            elif self.export_format == 'JSON':
                self.export_json(filepath, frames_data)
            
            self.report({'INFO'}, f"Motion data exported to: {filepath}")
            
            context.scene.frame_set(original_frame)
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error writing file: {str(e)}")
            
            context.scene.frame_set(original_frame)
            
            return {'CANCELLED'}
    
    def export_csv(self, filepath, animation_data):
        with open(filepath, 'w', newline='') as csvfile:
            if animation_data:
                fieldnames = animation_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(animation_data)
    
    def export_json(self, filepath, frames_data):
        first_frame = next(iter(frames_data.values()))
        bone_names = list(first_frame.keys())
        
        # Analyze bone hierarchy
        obj = bpy.context.active_object
        bone_groups = {}
        
        for bone_name in bone_names:
            if bone_name in obj.pose.bones:
                bone = obj.pose.bones[bone_name]
                
                # Try to determine bone type from name
                bone_type = "other"
                name_lower = bone_name.lower()
                
                if "arm" in name_lower or "hand" in name_lower or "finger" in name_lower or "thumb" in name_lower:
                    bone_type = "arm"
                elif "leg" in name_lower or "foot" in name_lower or "toe" in name_lower:
                    bone_type = "leg"
                elif "spine" in name_lower or "neck" in name_lower:
                    bone_type = "spine"
                elif "head" in name_lower or "face" in name_lower or "jaw" in name_lower:
                    bone_type = "head"
                elif "hip" in name_lower or "pelvis" in name_lower:
                    bone_type = "hip"
                
                if bone_type not in bone_groups:
                    bone_groups[bone_type] = []
                bone_groups[bone_type].append(bone_name)
        
        bones_data = {}
        for bone_type, bones in bone_groups.items():
            bones_data[bone_type] = {}
            for bone_name in bones:
                bones_data[bone_type][bone_name] = {
                    "frames": {}
                }
                for frame, frame_data in frames_data.items():
                    if bone_name in frame_data:
                        bones_data[bone_type][bone_name]["frames"][frame] = frame_data[bone_name]
        
        organized_data = {
            "metadata": {
                "format": "bone motion data in by frame and by bone type",
                "coordinate_system": self.coordinate_system.lower(),
                "frame_count": len(frames_data),
                "bone_count": len(bone_names),
                "frame_range": [int(min(frames_data.keys())), int(max(frames_data.keys()))]
            },
            "by_frame": frames_data,
            "by_bone_type": bones_data
        }
        
        with open(filepath, 'w') as jsonfile:
            json.dump(organized_data, jsonfile, indent=2)

def menu_func_export(self, context):
    self.layout.operator(BONE_OT_export_motion_data.bl_idname, text="Bone Motion Data")

classes = (
    BONE_OT_export_motion_data,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
