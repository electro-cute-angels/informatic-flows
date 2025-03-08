bl_info = {
    "name": "Bone Motion to CSV Exporter",
    "author": "electro-cute-angels",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Export > Bone Motion to CSV",
    "description": "Export bone motion data to CSV - part of 'informatic flows' series",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

import bpy
import csv
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
    
    items.insert(0, ("ALL", "All Bones", "Export motion from all bones (will create a wider CSV with multiple columns)"))
    
    if len(items) == 1:
        items.append(("NONE", "No Bones Found", "No bones found in the active armature"))
    
    return items

def get_animation_range(context):
    obj = context.active_object
    if obj and obj.animation_data and obj.animation_data.action:
        frame_range = obj.animation_data.action.frame_range
        return (int(frame_range[0]), int(frame_range[1]))
    return (1, 250)

class BONE_OT_export_animation_csv(Operator, ExportHelper):
    bl_idname = "export.bone_animation_csv"
    bl_label = "Export Bone Motion to CSV"
    
    filename_ext = ".csv"
    
    filter_glob: StringProperty(
        default="*.csv",
        options={'HIDDEN'},
        maxlen=255,
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
        start, end = get_animation_range(context)
        self.start_frame = start
        self.end_frame = end
        return super().invoke(context, event)
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Bone Motion Exporter ❦")
        
        box = layout.box()
        box.label(text="Bone Selection:")
        box.prop(self, "show_hidden_bones")
        box.prop(self, "bone_to_export")
        
        if self.bone_to_export == "ALL":
            box.label(text="Note: Exporting all bones will create a wide CSV", icon='INFO')
            box.label(text="with multiple columns for each bone.")
        
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
            with open(self.filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                if len(bones_to_export) == 1:
                    writer.writerow(["frame", "pos_x", "pos_y", "pos_z", "rot_x", "rot_y", "rot_z"])
                else:
                    header = ["frame"]
                    for bone in bones_to_export:
                        for suffix in ["pos_x", "pos_y", "pos_z", "rot_x", "rot_y", "rot_z"]:
                            header.append(f"{bone.name}_{suffix}")
                    writer.writerow(header)
                
                changed_values = 0
                last_values = None
                
                for frame in frames_to_sample:
                    context.scene.frame_set(frame)
                    context.view_layer.update()
                    
                    row_data = [frame]
                    all_raw_values = []
                    
                    for bone in bones_to_export:
                        bone_matrix = obj.matrix_world @ bone.matrix
                        
                        loc = bone_matrix.to_translation()
                        rot = bone_matrix.to_euler()
                        
                        raw_values = [loc.x, loc.y, loc.z, rot.x, rot.y, rot.z]
                        all_raw_values.extend(raw_values)
                        
                        if self.coordinate_system == 'WORLD':
                            for v in raw_values:
                                row_data.append(round(v, self.precision))
                        else:
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
                            
                            for v in norm_pos + norm_rot:
                                row_data.append(round(v, self.precision))
                    
                    if last_values:
                        has_changed = any(abs(a - b) > 0.0001 for a, b in zip(all_raw_values, last_values))
                        if has_changed:
                            changed_values += 1
                    else:
                        changed_values += 1
                    
                    last_values = all_raw_values
                    
                    writer.writerow(row_data)
            
            self.report({'INFO'}, f"Motion data exported to: {self.filepath}")
            
            context.scene.frame_set(original_frame)
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error writing CSV file: {str(e)}")
            
            context.scene.frame_set(original_frame)
            
            return {'CANCELLED'}

def menu_func_export(self, context):
    self.layout.operator(BONE_OT_export_animation_csv.bl_idname, text="Bone Motion to .CSV")

classes = (
    BONE_OT_export_animation_csv,
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