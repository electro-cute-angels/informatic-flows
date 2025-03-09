bl_info = {
    "name": "Bone Media Spawner",
    "author": "electro-cute-angels",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Bone Media",
    "description": "Create image or video planes that follow bones with advanced positioning options",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}

import bpy
import math
import random
import os
from mathutils import Vector, Matrix
from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty,
                      FloatVectorProperty, EnumProperty, CollectionProperty)
from bpy.types import Panel, Operator, PropertyGroup, UIList
from bpy_extras.io_utils import ImportHelper

# ------------------------------------------------------------------------------------------------
# Bone Selection Property Group
# ------------------------------------------------------------------------------------------------

class BoneItem(bpy.types.PropertyGroup):
    """A property for selecting bones in the UI"""
    selected: BoolProperty(
        name="Selected",
        description="Select this bone for media creation",
        default=False
    )
    
    image_path: StringProperty(
        name="Image Path",
        description="Path to the image/video for this bone",
        default=""
    )

# ------------------------------------------------------------------------------------------------
# Media Item Property Group
# ------------------------------------------------------------------------------------------------

class MediaItem(bpy.types.PropertyGroup):
    """A property for listing media files in the UI"""
    name: StringProperty(
        name="Name",
        description="Media file name",
        default=""
    )
    
    path: StringProperty(
        name="Path",
        description="Full path to media file",
        default=""
    )
    
    selected: BoolProperty(
        name="Selected",
        description="Select this media for assignment",
        default=False
    )
    
    bone_name: StringProperty(
        name="Assigned Bone",
        description="Name of the bone this media is assigned to",
        default=""
    )

# ------------------------------------------------------------------------------------------------
# Media Spawning Functions
# ------------------------------------------------------------------------------------------------

def get_media_files_from_directory(directory):
    """
    Get a list of image and video files from a directory
    
    Args:
        directory: Directory path to search
        
    Returns:
        List of file paths
    """
    media_extensions = {
        # Image formats
        '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.tga', '.exr', '.hdr',
        # Video formats
        '.mp4', '.mov', '.avi', '.mkv', '.webm'
    }
    
    media_files = []
    
    if os.path.exists(directory) and os.path.isdir(directory):
        for file in os.listdir(directory):
            if os.path.splitext(file)[1].lower() in media_extensions:
                media_files.append(os.path.join(directory, file))
                
    return media_files

def is_video_file(file_path):
    """Check if a file is a video format"""
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
    return os.path.splitext(file_path)[1].lower() in video_extensions

def create_media_plane(context, media_path, name):
    """
    Create a plane with the media as a texture
    
    Args:
        context: Blender context
        media_path: Path to the media file
        name: Name for the plane object
        
    Returns:
        Created plane object
    """
    # Create mesh and object
    bpy.ops.mesh.primitive_plane_add(size=1.0, enter_editmode=False, align='WORLD')
    plane_obj = context.active_object
    plane_obj.name = name
    
    # Add a material
    mat = bpy.data.materials.new(name=f"Material_{name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
        
    # Create nodes
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    emission_node = nodes.new(type='ShaderNodeEmission')
    tex_node = nodes.new(type='ShaderNodeTexImage')
    
    # Load the image
    is_video = is_video_file(media_path)
    if is_video:
        tex_node.image = bpy.data.images.load(media_path)
        tex_node.image_user.use_auto_refresh = True
        tex_node.image_user.frame_duration = 1000  # Default long duration
    else:
        tex_node.image = bpy.data.images.load(media_path)
    
    # Connect nodes
    links.new(tex_node.outputs["Color"], emission_node.inputs["Color"])
    links.new(emission_node.outputs["Emission"], output_node.inputs["Surface"])
    
    # Set emission strength
    emission_node.inputs["Strength"].default_value = 1.0
    
    # Assign material to object
    if plane_obj.data.materials:
        plane_obj.data.materials[0] = mat
    else:
        plane_obj.data.materials.append(mat)
    
    # Set display properties
    plane_obj.display_type = 'TEXTURED'
    
    # Set up the plane to face the correct direction (Z+ is forward)
    plane_obj.rotation_euler = (math.radians(90), 0, 0)
    
    return plane_obj

def create_bone_media_planes(context, bone_names, media_settings):
    """
    Create planes with media for each bone in the active armature
    
    Args:
        context: Blender context
        bone_names: Dictionary mapping bone names to media paths
        media_settings: Dictionary of media settings
        
    Returns:
        List of created plane objects
    """
    obj = context.active_object
    if not obj or obj.type != 'ARMATURE':
        return []
    
    pose_bones = obj.pose.bones
    bones_to_process = [bone for bone in pose_bones if bone.name in bone_names]
    
    if not bones_to_process:
        return []
    
    collection_name = f"{obj.name}_Bone_Media"
    if collection_name in bpy.data.collections:
        media_collection = bpy.data.collections[collection_name]
    else:
        media_collection = bpy.data.collections.new(collection_name)
        context.scene.collection.children.link(media_collection)
    
    media_distance = media_settings.get('distance', 4.0)
    media_scale = media_settings.get('scale', 1.0)
    position_type = media_settings.get('position_type', 'FRONT')
    position_axis = media_settings.get('position_axis', 'XYZ')
    custom_position = media_settings.get('custom_position', (0, 0, 0))
    custom_position_enabled = media_settings.get('custom_position_enabled', False)
    offset_position = media_settings.get('offset_position', (0, 0, 0))
    rotation_offset = media_settings.get('rotation_offset', (0, 0, 0))
    
    bone_media_planes = []
    
    for bone in bones_to_process:
        if bone.name not in bone_names or not bone_names[bone.name]:
            continue
            
        media_path = bone_names[bone.name]
        plane_name = f"Media_{bone.name}"
        
        # Check if the media plane already exists
        if plane_name in bpy.data.objects:
            # Remove old one to refresh the media
            old_obj = bpy.data.objects[plane_name]
            bpy.data.objects.remove(old_obj, do_unlink=True)
        
        # Create a new plane with the media
        media_plane = create_media_plane(context, media_path, plane_name)
        
        # Link to collection
        if media_plane.name in media_collection.objects:
            pass  # Already linked
        else:
            media_collection.objects.link(media_plane)
            if media_plane.name in context.collection.objects:
                context.collection.objects.unlink(media_plane)
        
        # Fixed scaling - consistent for all media types
        bone_length = (bone.tail - bone.head).length
        
        # Get image dimensions for aspect ratio
        aspect_ratio = 1.0
        try:
            if is_video_file(media_path):
                # Use 16:9 as standard aspect for videos
                aspect_ratio = 16.0 / 9.0
            else:
                # For images, get actual dimensions
                img = bpy.data.images.get(os.path.basename(media_path))
                if img and img.size[1] > 0:
                    aspect_ratio = img.size[0] / img.size[1]
        except:
            # Default to square if we can't determine
            aspect_ratio = 1.0
            
        # Apply consistent scaling
        scaled_height = media_scale
        scaled_width = media_scale * aspect_ratio
        media_plane.scale = (scaled_width, scaled_height, 1.0)
        
        # Apply rotation offset
        rot_x, rot_y, rot_z = rotation_offset
        media_plane.rotation_euler[0] += math.radians(rot_x)
        media_plane.rotation_euler[1] += math.radians(rot_y)
        media_plane.rotation_euler[2] += math.radians(rot_z)
        
        # Clear any existing constraints
        for constraint in media_plane.constraints[:]:
            media_plane.constraints.remove(constraint)
        
        # Get bone world coordinates
        bone_head_world = obj.matrix_world @ bone.head
        bone_tail_world = obj.matrix_world @ bone.tail
        bone_mid = (bone_head_world + bone_tail_world) / 2
        bone_dir = (bone_tail_world - bone_head_world).normalized()
        
        # Create an empty for the offset target
        empty_name = f"Offset_{bone.name}"
        if empty_name in bpy.data.objects:
            offset_empty = bpy.data.objects[empty_name]
        else:
            bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.1)
            offset_empty = context.active_object
            offset_empty.name = empty_name
            
            # Link empty to collection
            if offset_empty.name in media_collection.objects:
                pass
            else:
                media_collection.objects.link(offset_empty)
                if offset_empty.name in context.collection.objects:
                    context.collection.objects.unlink(offset_empty)
        
        # Determine the base position without offset
        if position_type == 'HEAD':
            base_pos = bone_head_world
        elif position_type == 'TAIL':
            base_pos = bone_tail_world
        else:
            base_pos = bone_mid
        
        # Apply distance offset based on position type
        if media_distance == 0:
            # When distance is 0, place directly at base position
            offset_empty.location = base_pos
        elif custom_position_enabled:
            # Use custom position
            offset_empty.location = Vector(custom_position)
        else:
            if position_type == 'RANDOM':
                # Random direction offset
                random_dir = Vector((
                    random.uniform(-1, 1),
                    random.uniform(-1, 1),
                    random.uniform(-1, 1)
                )).normalized()
                offset_empty.location = base_pos + random_dir * media_distance
                
            elif position_type == 'ALIGNED':
                # Aligned along specific axis
                if position_axis == 'X':
                    offset_vec = Vector((1, 0, 0)) * media_distance
                elif position_axis == 'Y':
                    offset_vec = Vector((0, 1, 0)) * media_distance
                elif position_axis == 'Z':
                    offset_vec = Vector((0, 0, 1)) * media_distance
                elif position_axis == 'XY':
                    offset_vec = Vector((1, 1, 0)).normalized() * media_distance
                elif position_axis == 'XZ':
                    offset_vec = Vector((1, 0, 1)).normalized() * media_distance
                elif position_axis == 'YZ':
                    offset_vec = Vector((0, 1, 1)).normalized() * media_distance
                else:  # 'XYZ'
                    offset_vec = Vector((1, 1, 1)).normalized() * media_distance
                
                offset_empty.location = base_pos + offset_vec
                
            elif position_type == 'PERPENDICULAR':
                # Perpendicular to bone direction
                world_up = Vector((0, 0, 1))
                perp_vector = bone_dir.cross(world_up)
                if perp_vector.length < 0.01:
                    world_up = Vector((0, 1, 0))
                    perp_vector = bone_dir.cross(world_up)
                
                perp_vector.normalize()
                offset_empty.location = base_pos + perp_vector * media_distance
                
            elif position_type == 'ANGLED':
                # 45-degree angle offset
                offset_vec = Vector((1, 1, 1)).normalized() * media_distance
                offset_empty.location = base_pos + offset_vec
                
            else:  # 'FRONT' or default
                # Default Z-axis offset
                offset_vec = Vector((0, 0, 1)) * media_distance
                offset_empty.location = base_pos + offset_vec
            
        # Apply any additional position offset
        offset_empty.location += Vector(offset_position)
        
        # Create constraints
        
        # First, create a constraint for the empty to follow the bone
        for constraint in offset_empty.constraints[:]:
            offset_empty.constraints.remove(constraint)
            
        if media_distance > 0 or custom_position_enabled:
            # We need to use constraints to keep the distance consistent
            copy_rot = offset_empty.constraints.new('COPY_ROTATION')
            copy_rot.target = obj
            copy_rot.subtarget = bone.name
            
            # Make the media plane follow the empty (maintaining distance)
            copy_loc = media_plane.constraints.new('COPY_LOCATION')
            copy_loc.target = offset_empty
            
            # Make the media plane face the bone
            track_to = media_plane.constraints.new('TRACK_TO')
            track_to.target = obj
            track_to.subtarget = bone.name
            track_to.track_axis = 'TRACK_NEGATIVE_Z'
            track_to.up_axis = 'UP_Y'
            
        else:
            # For zero distance, attach directly to bone
            copy_loc = media_plane.constraints.new('COPY_LOCATION')
            copy_loc.target = obj
            copy_loc.subtarget = bone.name
            
            if position_type == 'HEAD':
                copy_loc.head_tail = 0.0
            elif position_type == 'TAIL':
                copy_loc.head_tail = 1.0
            else: 
                copy_loc.head_tail = 0.5
            
            copy_rot = media_plane.constraints.new('COPY_ROTATION')
            copy_rot.target = obj
            copy_rot.subtarget = bone.name
        
        bone_media_planes.append(media_plane)
    
    return bone_media_planes

def populate_bone_items(scene, armature):
    """Populate the bone items collection"""
    if not armature or armature.type != 'ARMATURE':
        return
    
    # Store current selected state if items exist
    selected_bones = {}
    image_paths = {}
    if hasattr(scene, "bone_media_items"):
        for item in scene.bone_media_items:
            selected_bones[item.name] = item.selected
            image_paths[item.name] = item.image_path
    
    # Clear and repopulate
    if hasattr(scene, "bone_media_items"):
        scene.bone_media_items.clear()
    
    for bone in armature.pose.bones:
        item = scene.bone_media_items.add()
        item.name = bone.name
        # Restore selection state if it existed before
        if bone.name in selected_bones:
            item.selected = selected_bones[bone.name]
            item.image_path = image_paths[bone.name]
        else:
            item.selected = False
            item.image_path = ""

def populate_media_items(scene, media_files):
    """Populate the media items collection"""
    scene.media_items.clear()
    
    for media_path in media_files:
        item = scene.media_items.add()
        item.name = os.path.basename(media_path)
        item.path = media_path
        item.selected = False
        item.bone_name = ""
    
    # Sort by name
    sorted_items = sorted([(i, item.name) for i, item in enumerate(scene.media_items)], key=lambda x: x[1])
    
    # Create a temporary list and repopulate in sorted order
    temp_items = []
    for i, _ in sorted_items:
        temp_items.append((scene.media_items[i].name, scene.media_items[i].path))
    
    scene.media_items.clear()
    for name, path in temp_items:
        item = scene.media_items.add()
        item.name = name
        item.path = path
        item.selected = False
        item.bone_name = ""

# ------------------------------------------------------------------------------------------------
# Operators
# ------------------------------------------------------------------------------------------------

class VIEW3D_OT_select_media_folder(bpy.types.Operator, ImportHelper):
    """Select a folder containing media files"""
    bl_idname = "view3d.select_media_folder"
    bl_label = "Select Media Folder"
    
    directory: StringProperty(
        name="Directory",
        subtype='DIR_PATH',
    )
    
    filename_ext = ""
    use_filter_folder = True
    
    def execute(self, context):
        if not os.path.isdir(self.directory):
            self.report({'WARNING'}, "The selected path is not a directory")
            return {'CANCELLED'}
        
        media_files = get_media_files_from_directory(self.directory)
        
        if not media_files:
            self.report({'WARNING'}, "No supported media files found in the selected directory")
            return {'CANCELLED'}
        
        # Store the directory
        context.scene.bone_media_directory = self.directory
        
        # Populate media items
        populate_media_items(context.scene, media_files)
        
        self.report({'INFO'}, f"Found {len(media_files)} media files in {os.path.basename(self.directory)}")
        return {'FINISHED'}

class VIEW3D_OT_assign_random_media(bpy.types.Operator):
    """Assign random media files to selected bones"""
    bl_idname = "view3d.assign_random_media"
    bl_label = "Assign Random Media"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get selected bones
        selected_bones = [item for item in context.scene.bone_media_items if item.selected]
        
        if not selected_bones:
            self.report({'WARNING'}, "No bones selected. Please select at least one bone.")
            return {'CANCELLED'}
        
        # Get available media
        media_items = [item for item in context.scene.media_items if item.path]
        
        if not media_items:
            self.report({'WARNING'}, "No media files available. Please select a folder with media files.")
            return {'CANCELLED'}
        
        # Clear previous bone assignments
        for media_item in context.scene.media_items:
            media_item.bone_name = ""
        
        # Assign random media to each selected bone
        assigned_count = 0
        for bone_item in selected_bones:
            random_media = random.choice(media_items)
            bone_item.image_path = random_media.path
            
            # Update the media item to show bone assignment
            # If a media is used multiple times, we'll just show the last bone
            random_media.bone_name = bone_item.name
            assigned_count += 1
        
        self.report({'INFO'}, f"Randomly assigned media to {assigned_count} bones")
        return {'FINISHED'}

class VIEW3D_OT_assign_specific_media(bpy.types.Operator):
    """Assign specific media files to selected bones"""
    bl_idname = "view3d.assign_specific_media"
    bl_label = "Assign Selected Media"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get selected bones
        selected_bones = [item for item in context.scene.bone_media_items if item.selected]
        
        if not selected_bones:
            self.report({'WARNING'}, "No bones selected. Please select at least one bone.")
            return {'CANCELLED'}
        
        # Get selected media
        selected_media = [item for item in context.scene.media_items if item.selected]
        
        if not selected_media:
            self.report({'WARNING'}, "No media files selected. Please select at least one media file.")
            return {'CANCELLED'}
        
        # Clear previous bone assignments
        for media_item in context.scene.media_items:
            if media_item.selected:
                media_item.bone_name = ""
        
        # Check if we're in one-to-one or one-to-many mode
        if len(selected_media) == 1:
            # Assign the same media to all selected bones
            media_path = selected_media[0].path
            media_name = selected_media[0].name
            
            for bone_item in selected_bones:
                bone_item.image_path = media_path
                
                # Update the media item to show bone assignment
                selected_media[0].bone_name = f"Multiple ({len(selected_bones)})"
            
            self.report({'INFO'}, f"Assigned '{media_name}' to {len(selected_bones)} bones")
        else:
            # Try to assign media one-to-one
            if len(selected_media) < len(selected_bones):
                self.report({'WARNING'}, f"Only {len(selected_media)} media files for {len(selected_bones)} bones. Some bones will not get media.")
            
            for i, bone_item in enumerate(selected_bones):
                if i < len(selected_media):
                    bone_item.image_path = selected_media[i].path
                    selected_media[i].bone_name = bone_item.name
            
            self.report({'INFO'}, f"Assigned {min(len(selected_bones), len(selected_media))} media files to bones")
        
        return {'FINISHED'}

class VIEW3D_OT_create_bone_media(bpy.types.Operator):
    """Create media planes for selected bones in the active armature"""
    bl_idname = "view3d.create_bone_media"
    bl_label = "Create Media Planes"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get selected bones and their assigned media
        bone_media_map = {}
        for item in context.scene.bone_media_items:
            if item.selected and item.image_path:
                bone_media_map[item.name] = item.image_path
        
        if not bone_media_map:
            self.report({'WARNING'}, "No bones with assigned media selected. Please select at least one bone with media.")
            return {'CANCELLED'}
        
        media_settings = {
            'distance': context.scene.bone_media_distance,
            'scale': context.scene.bone_media_scale,
            'position_type': context.scene.bone_media_position_type,
            'position_axis': context.scene.bone_media_position_axis,
            'custom_position': context.scene.bone_media_custom_position,
            'custom_position_enabled': context.scene.bone_media_custom_position_enabled,
            'offset_position': context.scene.bone_media_offset_position,
            'rotation_offset': context.scene.bone_media_rotation_offset
        }
        
        media_planes = create_bone_media_planes(
            context,
            bone_media_map,
            media_settings
        )
        
        if not media_planes:
            self.report({'WARNING'}, "No media planes were created.")
            return {'CANCELLED'}
        
        self.report({'INFO'}, f"Created {len(media_planes)} media planes")
        return {'FINISHED'}

class VIEW3D_OT_clear_media_planes(bpy.types.Operator):
    """Remove all media planes from the scene"""
    bl_idname = "view3d.clear_media_planes"
    bl_label = "Clear All Media Planes"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'WARNING'}, "No armature selected.")
            return {'CANCELLED'}
        
        collection_name = f"{obj.name}_Bone_Media"
        if collection_name in bpy.data.collections:
            collection = bpy.data.collections[collection_name]
            
            # Get all objects in the collection
            objects_to_remove = [o for o in collection.objects]
            
            # Remove all objects
            for o in objects_to_remove:
                bpy.data.objects.remove(o, do_unlink=True)
            
            # Remove the collection
            bpy.data.collections.remove(collection)
            
            self.report({'INFO'}, f"Removed {len(objects_to_remove)} media planes")
        else:
            self.report({'INFO'}, "No media planes found to remove")
        
        return {'FINISHED'}

class VIEW3D_OT_select_all_bones(bpy.types.Operator):
    """Select all bones in the list"""
    bl_idname = "bone_media.select_all_bones"
    bl_label = "Select All Bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for item in context.scene.bone_media_items:
            item.selected = True
        return {'FINISHED'}

class VIEW3D_OT_select_none_bones(bpy.types.Operator):
    """Deselect all bones in the list"""
    bl_idname = "bone_media.select_none_bones"
    bl_label = "Deselect All Bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for item in context.scene.bone_media_items:
            item.selected = False
        return {'FINISHED'}

class VIEW3D_OT_select_all_media(bpy.types.Operator):
    """Select all media in the list"""
    bl_idname = "bone_media.select_all_media"
    bl_label = "Select All Media"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for item in context.scene.media_items:
            item.selected = True
        return {'FINISHED'}

class VIEW3D_OT_select_none_media(bpy.types.Operator):
    """Deselect all media in the list"""
    bl_idname = "bone_media.select_none_media"
    bl_label = "Deselect All Media"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for item in context.scene.media_items:
            item.selected = False
        return {'FINISHED'}

# ------------------------------------------------------------------------------------------------
# UI Classes
# ------------------------------------------------------------------------------------------------

class BONE_UL_media_item(bpy.types.UIList):
    """UI list for displaying bones with checkboxes and assigned media"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.7)
            
            # Left side with bone selection and name
            row = split.row(align=True)
            row.prop(item, "selected", text="")
            row.label(text=item.name)
            
            # Right side with media info
            media_row = split.row(align=True)
            if item.image_path:
                filename = os.path.basename(item.image_path)
                if len(filename) > 15:
                    filename = filename[:12] + "..."
                media_row.label(text=filename, icon='FILE_IMAGE')
            else:
                media_row.label(text="No media", icon='X')
        
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "selected", text="")

class MEDIA_UL_item(bpy.types.UIList):
    """UI list for displaying media files with checkboxes"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.8)
            
            # Left side with media selection and name
            row = split.row(align=True)
            row.prop(item, "selected", text="")
            
            # Determine icon based on file type
            media_icon = 'FILE_IMAGE'
            if os.path.splitext(item.name)[1].lower() in {'.mp4', '.mov', '.avi', '.mkv', '.webm'}:
                media_icon = 'SEQUENCE'
                
            row.label(text=item.name, icon=media_icon)
            
            # Right side with assignment info
            info_row = split.row(align=True)
            if item.bone_name:
                info_row.label(text=item.bone_name, icon='BONE_DATA')
        
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "selected", text="")

class VIEW3D_OT_refresh_bone_list(bpy.types.Operator):
    """Refresh the bone list from the active armature"""
    bl_idname = "view3d.refresh_bone_list"
    bl_label = "Refresh Bone List"
    
    def execute(self, context):
        populate_bone_items(context.scene, context.active_object)
        context.scene.needs_bone_refresh = False
        return {'FINISHED'}

class VIEW3D_PT_bone_media(bpy.types.Panel):
    """Bone Media Creator Panel"""
    bl_label = "Bone Media Spawner"
    bl_idname = "VIEW3D_PT_bone_media"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bone Media'
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Check if we need to update bone list
        if scene.needs_bone_refresh:
            box = layout.box()
            box.label(text="Initialize Bone List", icon='ERROR')
            box.operator("view3d.refresh_bone_list", text="Load Bones from Armature", icon='ARMATURE_DATA')
            return  # Don't show the rest of the UI until bones are loaded
        
        # Media Directory Selection
        box = layout.box()
        box.label(text="Media Source:", icon='FOLDER_REDIRECT')
        
        row = box.row(align=True)
        # Use a text field without a built-in folder icon
        row.prop(scene, "bone_media_directory", text="")
        # Add a browse button
        row.operator("view3d.select_media_folder", text="Browse", icon='FILEBROWSER')
        
        # Media Files Box
        if len(scene.media_items) > 0:
            box = layout.box()
            box.label(text="Available Media Files:", icon='FILE_IMAGE')
            
            row = box.row(align=True)
            row.operator("bone_media.select_all_media", text="Select All")
            row.operator("bone_media.select_none_media", text="Select None")
            
            # Show count of selected media
            selected_count = sum(1 for item in scene.media_items if item.selected)
            box.label(text=f"Selected: {selected_count}/{len(scene.media_items)}")
            
            col = box.column(align=True)
            col.template_list("MEDIA_UL_item", "", scene, "media_items", scene, "media_items_index", rows=3)
            
            # Bone Selection
            box = layout.box()
            box.label(text="Select Bones:", icon='BONE_DATA')
            
            row = box.row(align=True)
            row.operator("bone_media.select_all_bones", text="Select All")
            row.operator("bone_media.select_none_bones", text="Select None")
            
            # Show count of selected bones
            selected_bones = sum(1 for item in scene.bone_media_items if item.selected)
            box.label(text=f"Selected: {selected_bones}/{len(scene.bone_media_items)}")
            
            col = box.column(align=True)
            col.template_list("BONE_UL_media_item", "", scene, "bone_media_items", scene, "bone_media_items_index", rows=3)
            
            # Media assignment operations - only show if both bones and media are selected
            if selected_count > 0 and selected_bones > 0:
                box = layout.box()
                box.label(text="Assign Media to Bones:", icon='CONSTRAINT')
                
                col = box.column(align=True)
                row = col.row(align=True)
                row.operator("view3d.assign_random_media", text="Random Assignment", icon='SCULPTMODE_HLT')
                row.operator("view3d.assign_specific_media", text="Assign Selected", icon='PIVOT_INDIVIDUAL')
                
                # Help text for assignment
                if selected_count == 1:
                    box.label(text="Single media will be assigned to all selected bones")
                elif selected_count > selected_bones:
                    box.label(text="One media per bone will be assigned in order")
                elif selected_count < selected_bones:
                    box.label(text="Warning: Some bones won't receive media")
        else:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="No media files found", icon='ERROR')
            col.label(text="Please select a folder with images/videos")
            
        # Only show media plane settings and creation if some bones have media assigned
        has_assigned_media = False
        for item in scene.bone_media_items:
            if item.selected and item.image_path:
                has_assigned_media = True
                break
        
        if has_assigned_media:
            # Media Plane Settings
            box = layout.box()
            box.label(text="Media Plane Settings:", icon='MESH_PLANE')
            
            col = box.column(align=True)
            col.prop(scene, "bone_media_distance", text="Distance from Bone")
            col.prop(scene, "bone_media_scale", text="Scale Factor")
            
            col.label(text="Position Settings:")
            col.prop(scene, "bone_media_position_type", text="Position")
            
            # Media plane settings - show more options based on position type
            if scene.bone_media_position_type == 'ALIGNED':
                col.prop(scene, "bone_media_position_axis", text="Align to")
            
            # Show additional info based on position type
            if scene.bone_media_position_type == 'RANDOM':
                col.label(text="Note: Random places media in random directions")
            elif scene.bone_media_position_type == 'PERPENDICULAR':
                col.label(text="Note: Perpendicular to bone direction")
            elif scene.bone_media_position_type == 'ANGLED':
                col.label(text="Note: 45-degree angle to bone")
            
            col.prop(scene, "bone_media_custom_position_enabled", text="Use Custom Position")
            if scene.bone_media_custom_position_enabled:
                subcol = col.column(align=True)
                subcol.prop(scene, "bone_media_custom_position", text="")
            
            col.label(text="Fine Adjustments:")
            col.prop(scene, "bone_media_offset_position", text="Position Offset")
            col.prop(scene, "bone_media_rotation_offset", text="Rotation Offset")
            
            # Create/Clear Media Planes
            box = layout.box()
            col = box.column(align=True)
            col.operator("view3d.create_bone_media", text="Create Media Planes", icon='ADD')
            col.operator("view3d.clear_media_planes", text="Clear All Media Planes", icon='X')

# ------------------------------------------------------------------------------------------------
# Event Handler
# ------------------------------------------------------------------------------------------------

@bpy.app.handlers.persistent
def update_bone_items_handler(scene, depsgraph):
    """Safe handler for updating bone items when the active object changes"""
    # We'll just set a flag that the armature changed, but won't modify collections in the handler
    if bpy.context.active_object and bpy.context.active_object.type == 'ARMATURE':
        if not scene.get('active_armature') or scene['active_armature'] != bpy.context.active_object.name:
            scene['active_armature'] = bpy.context.active_object.name
            scene.needs_bone_refresh = True

# ------------------------------------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------------------------------------

classes = (
    BoneItem,
    MediaItem,
    BONE_UL_media_item,
    MEDIA_UL_item,
    VIEW3D_PT_bone_media,
    VIEW3D_OT_refresh_bone_list,
    VIEW3D_OT_select_media_folder,
    VIEW3D_OT_assign_random_media,
    VIEW3D_OT_assign_specific_media,
    VIEW3D_OT_create_bone_media,
    VIEW3D_OT_clear_media_planes,
    VIEW3D_OT_select_all_bones,
    VIEW3D_OT_select_none_bones,
    VIEW3D_OT_select_all_media,
    VIEW3D_OT_select_none_media
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register properties
    bpy.types.Scene.bone_media_items = bpy.props.CollectionProperty(type=BoneItem)
    bpy.types.Scene.bone_media_items_index = bpy.props.IntProperty(default=0)
    
    bpy.types.Scene.media_items = bpy.props.CollectionProperty(type=MediaItem)
    bpy.types.Scene.media_items_index = bpy.props.IntProperty(default=0)
    
    # Register the needs_bone_refresh property properly
    bpy.types.Scene.needs_bone_refresh = bpy.props.BoolProperty(default=True)
    
    bpy.types.Scene.bone_media_directory = bpy.props.StringProperty(
        name="Media Directory",
        description="Directory containing media files",
        default="",
        subtype='DIR_PATH'
    )
    
    bpy.types.Scene.bone_media_distance = bpy.props.FloatProperty(
        name="Distance",
        description="Distance from bone to place media",
        default=1.0,
        min=0.0,
        max=10.0
    )
    
    bpy.types.Scene.bone_media_scale = bpy.props.FloatProperty(
        name="Scale",
        description="Scale factor for media planes",
        default=1.0,
        min=0.1,
        max=10.0
    )
    
    bpy.types.Scene.bone_media_position_type = bpy.props.EnumProperty(
        name="Position Type",
        description="How to position the media relative to the bone",
        items=[
            ('FRONT', "Front", "Position in front of the bone"),
            ('HEAD', "Head", "Position at the head of the bone"),
            ('TAIL', "Tail", "Position at the tail of the bone"),
            ('ALIGNED', "Aligned", "Position along specific axes")
        ],
        default='FRONT'
    )
    
    bpy.types.Scene.bone_media_position_axis = bpy.props.EnumProperty(
        name="Alignment Axis",
        description="Which axis or plane to align the media to",
        items=[
            ('XYZ', "XYZ", "Diagonal in 3D space"),
            ('X', "X", "Along X axis"),
            ('Y', "Y", "Along Y axis"),
            ('Z', "Z", "Along Z axis"),
            ('XY', "XY", "In XY plane"),
            ('XZ', "XZ", "In XZ plane"),
            ('YZ', "YZ", "In YZ plane")
        ],
        default='Z'
    )
    
    bpy.types.Scene.bone_media_custom_position_enabled = bpy.props.BoolProperty(
        name="Use Custom Position",
        description="Use a custom fixed position offset for all media",
        default=False
    )
    
    bpy.types.Scene.bone_media_custom_position = bpy.props.FloatVectorProperty(
        name="Custom Position",
        description="Custom position offset for all media",
        default=(0.0, 0.0, 1.0),
        subtype='TRANSLATION'
    )
    
    bpy.types.Scene.bone_media_offset_position = bpy.props.FloatVectorProperty(
        name="Position Offset",
        description="Fine-tune position offset",
        default=(0.0, 0.0, 0.0),
        subtype='TRANSLATION'
    )
    
    bpy.types.Scene.bone_media_rotation_offset = bpy.props.FloatVectorProperty(
        name="Rotation Offset",
        description="Rotation offset in degrees",
        default=(0.0, 0.0, 0.0),
        subtype='EULER'
    )
    
    bpy.app.handlers.depsgraph_update_post.append(update_bone_items_handler)

def unregister():
    if update_bone_items_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_bone_items_handler)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.bone_media_items
    del bpy.types.Scene.bone_media_items_index
    del bpy.types.Scene.media_items
    del bpy.types.Scene.media_items_index
    del bpy.types.Scene.bone_media_directory
    del bpy.types.Scene.bone_media_distance
    del bpy.types.Scene.bone_media_scale
    del bpy.types.Scene.bone_media_position_type
    del bpy.types.Scene.bone_media_position_axis
    del bpy.types.Scene.bone_media_custom_position_enabled
    del bpy.types.Scene.bone_media_custom_position
    del bpy.types.Scene.bone_media_offset_position
    del bpy.types.Scene.bone_media_rotation_offset
    del bpy.types.Scene.needs_bone_refresh

if __name__ == "__main__":
    register()