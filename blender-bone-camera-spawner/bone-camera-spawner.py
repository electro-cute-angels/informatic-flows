bl_info = {
    "name": "Bone Camera Spawner",
    "author": "electro-cute-angels",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Bone Cameras",
    "description": "Create cameras targeting bones with advanced positioning options",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}

import bpy
import math
import random
from mathutils import Vector, Matrix

class BoneItem(bpy.types.PropertyGroup):
    """A property for selecting bones in the UI"""
    selected: bpy.props.BoolProperty(
        name="Selected",
        description="Select this bone for camera creation",
        default=False
    )

def create_bone_cameras(context, bone_names, camera_settings):
    """
    Create cameras targeting each bone in the active armature

    Args:
        context: Blender context
        bone_names: List of bone names to create cameras for
        camera_settings: Dictionary of camera settings

    Returns:
        List of created camera objects
    """

    obj = context.active_object
    if not obj or obj.type != 'ARMATURE':
        return []

    pose_bones = obj.pose.bones
    bones_to_process = [bone for bone in pose_bones if bone.name in bone_names]

    if not bones_to_process:
        return []

    collection_name = f"{obj.name}_Bone_Cameras"
    if collection_name in bpy.data.collections:
        cameras_collection = bpy.data.collections[collection_name]
    else:
        cameras_collection = bpy.data.collections.new(collection_name)
        context.scene.collection.children.link(cameras_collection)

    cam_distance = camera_settings.get('distance', 4.0)
    cam_type = camera_settings.get('type', 'PERSP')
    cam_lens = camera_settings.get('lens', 35.0)
    cam_ortho_scale = camera_settings.get('ortho_scale', 6.0)
    position_type = camera_settings.get('position_type', 'ANGLED')
    position_axis = camera_settings.get('position_axis', 'XYZ')
    custom_position = camera_settings.get('custom_position', (0, 0, 0))
    custom_position_enabled = camera_settings.get('custom_position_enabled', False)
    is_first_person = camera_settings.get('first_person', False)
    bone_attach_point = camera_settings.get('bone_attach_point', 'HEAD')

    bone_cameras = []
    for bone in bones_to_process:

        bone_length = (bone.tail - bone.head).length
        if bone_length < 0.001:
            continue

        camera_name = f"Camera_{bone.name}"
        if camera_name in bpy.data.objects:
            cam_obj = bpy.data.objects[camera_name]
            cam_data = cam_obj.data
        else:
            cam_data = bpy.data.cameras.new(name=camera_name)
            cam_obj = bpy.data.objects.new(name=camera_name, object_data=cam_data)
            cameras_collection.objects.link(cam_obj)

        cam_data.type = 'ORTHO' if cam_type == 'ORTHO' else 'PERSP'
        if cam_type == 'ORTHO':
            cam_data.ortho_scale = cam_ortho_scale * bone_length
        else:
            cam_data.lens = cam_lens
        cam_data.clip_start = 0.01
        cam_data.clip_end = 1000.0
        cam_data.display_size = 0.5  

        bone_head_world = obj.matrix_world @ bone.head
        bone_tail_world = obj.matrix_world @ bone.tail

        bone_mid = (bone_head_world + bone_tail_world) / 2
        bone_dir = (bone_tail_world - bone_head_world).normalized()

        camera_distance = max(1.0, bone_length * cam_distance)

        for constraint in cam_obj.constraints[:]:
            cam_obj.constraints.remove(constraint)

        if is_first_person:

            copy_loc = cam_obj.constraints.new('COPY_LOCATION')
            copy_loc.target = obj
            copy_loc.subtarget = bone.name

            if bone_attach_point == 'HEAD':
                copy_loc.head_tail = 0.0  
            elif bone_attach_point == 'TAIL':
                copy_loc.head_tail = 1.0  
            else:  
                copy_loc.head_tail = 0.5  

            copy_rot = cam_obj.constraints.new('COPY_ROTATION')
            copy_rot.target = obj
            copy_rot.subtarget = bone.name

            if bone_attach_point == 'TAIL':

                cam_obj.rotation_euler = (0, math.radians(180), 0)

            cam_obj.location = (0, 0, 0)

        else:

            if custom_position_enabled:

                cam_obj.location = Vector(custom_position)
            else:
                if position_type == 'RANDOM':

                    random_offset = Vector((
                        random.uniform(-1, 1), 
                        random.uniform(-1, 1), 
                        random.uniform(-1, 1)
                    )).normalized() * camera_distance
                    cam_obj.location = bone_mid + random_offset

                elif position_type == 'ALIGNED':

                    if position_axis == 'X':

                        cam_offset = Vector((1, 0, 0)) * camera_distance
                    elif position_axis == 'Y':

                        cam_offset = Vector((0, 1, 0)) * camera_distance
                    elif position_axis == 'Z':

                        cam_offset = Vector((0, 0, 1)) * camera_distance
                    elif position_axis == 'XY':

                        cam_offset = Vector((1, 1, 0)).normalized() * camera_distance
                    elif position_axis == 'XZ':

                        cam_offset = Vector((1, 0, 1)).normalized() * camera_distance
                    elif position_axis == 'YZ':

                        cam_offset = Vector((0, 1, 1)).normalized() * camera_distance
                    else:  

                        cam_offset = Vector((1, 1, 1)).normalized() * camera_distance

                    cam_obj.location = bone_mid + cam_offset

                elif position_type == 'PERPENDICULAR':

                    world_up = Vector((0, 0, 1))
                    perp_vector = bone_dir.cross(world_up)
                    if perp_vector.length < 0.01:

                        world_up = Vector((0, 1, 0))
                        perp_vector = bone_dir.cross(world_up)

                    perp_vector.normalize()
                    cam_obj.location = bone_mid + perp_vector * camera_distance

                else:  

                    cam_offset = Vector((1, 1, 1)).normalized() * camera_distance
                    cam_obj.location = bone_mid + cam_offset

            track_to = cam_obj.constraints.new('TRACK_TO')
            track_to.target = obj
            track_to.subtarget = bone.name  
            track_to.track_axis = 'TRACK_NEGATIVE_Z'  
            track_to.up_axis = 'UP_Y'  

        bone_cameras.append(cam_obj)

    return bone_cameras

def populate_bone_items(scene, armature):
    """Populate the bone items collection"""
    if not armature or armature.type != 'ARMATURE':
        return

    scene.bone_items.clear()

    for bone in armature.pose.bones:
        item = scene.bone_items.add()
        item.name = bone.name
        item.selected = False  

@bpy.app.handlers.persistent
def update_bone_items_handler(scene, depsgraph):
    """Safe handler for updating bone items when the active object changes"""
    if bpy.context.active_object and bpy.context.active_object.type == 'ARMATURE':

        if not scene.get('active_armature') or scene['active_armature'] != bpy.context.active_object.name:
            scene['active_armature'] = bpy.context.active_object.name
            populate_bone_items(scene, bpy.context.active_object)

def update_position_type(self, context):
    """Update visibility of axis selection based on position type"""
    position_type = context.scene.bone_camera_position_type

    context.scene.bone_camera_custom_position_enabled = False

def update_first_person(self, context):
    """Update when first person toggle changes"""
    if self.bone_camera_first_person:

        context.scene.bone_camera_custom_position_enabled = False

class VIEW3D_PT_bone_cameras(bpy.types.Panel):
    """Bone Camera Creator Panel"""
    bl_label = "Bone Camera Spawner"
    bl_idname = "VIEW3D_PT_bone_cameras"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bone Cameras'

    @classmethod
    def poll(cls, context):

        return context.active_object and context.active_object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if not scene.bone_items:
            populate_bone_items(scene, context.active_object)

        box = layout.box()
        box.label(text="Create Bone Cameras")

        col = box.column(align=True)
        col.prop(scene, "bone_camera_distance", text="Camera Distance")

        box.label(text="Camera Settings:")
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(scene, "bone_camera_type", expand=True)

        if scene.bone_camera_type == 'ORTHO':
            col.prop(scene, "bone_camera_ortho_scale", text="Ortho Scale")
        else:
            col.prop(scene, "bone_camera_lens", text="Focal Length")

        box.label(text="Camera Position:")
        col = box.column(align=True)
        col.prop(scene, "bone_camera_first_person", text="Bone Perspective")

        if scene.bone_camera_first_person:
            col.prop(scene, "bone_camera_attach_point", text="Attach to")
        else:

            col.prop(scene, "bone_camera_position_type", text="Position Type")

            if scene.bone_camera_position_type == 'ALIGNED':
                col.prop(scene, "bone_camera_position_axis", text="Align to")

            col.prop(scene, "bone_camera_custom_position_enabled", text="Use Custom Position")
            if scene.bone_camera_custom_position_enabled:
                subcol = col.column(align=True)
                subcol.prop(scene, "bone_camera_custom_position", text="")

        row = box.row(align=True)
        row.operator("bone_camera.select_all_bones", text="Select All")
        row.operator("bone_camera.select_none_bones", text="Select None")

        box.label(text="Select Bones:")
        col = box.column(align=True)
        col.template_list("BONE_UL_item", "", scene, "bone_items", scene, "bone_items_index", rows=3)

        box.operator("view3d.create_bone_cameras", text="Create Cameras")

        box = layout.box()
        box.label(text="Camera Navigation")

        bone_cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA' and "Camera_" in obj.name]

        if bone_cameras:
            col = box.column(align=True)
            for cam in bone_cameras:
                row = col.row(align=True)
                op = row.operator("view3d.set_active_camera", text=cam.name[7:])
                op.camera_name = cam.name
        else:
            box.label(text="No bone cameras found")

class BONE_UL_item(bpy.types.UIList):
    """UI list for displaying bones with checkboxes"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "selected", text="")
            layout.label(text=item.name)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "selected", text="")

class VIEW3D_OT_create_bone_cameras(bpy.types.Operator):
    """Create cameras for selected bones in the active armature"""
    bl_idname = "view3d.create_bone_cameras"
    bl_label = "Create Bone Cameras"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        selected_bones = [item.name for item in context.scene.bone_items if item.selected]

        if not selected_bones:
            self.report({'WARNING'}, "No bones selected. Please select at least one bone.")
            return {'CANCELLED'}

        camera_settings = {
            'distance': context.scene.bone_camera_distance,
            'type': context.scene.bone_camera_type,
            'lens': context.scene.bone_camera_lens,
            'ortho_scale': context.scene.bone_camera_ortho_scale,
            'position_type': context.scene.bone_camera_position_type,
            'position_axis': context.scene.bone_camera_position_axis,
            'custom_position': context.scene.bone_camera_custom_position,
            'custom_position_enabled': context.scene.bone_camera_custom_position_enabled,
            'first_person': context.scene.bone_camera_first_person,
            'bone_attach_point': context.scene.bone_camera_attach_point
        }

        cameras = create_bone_cameras(
            context,
            selected_bones,
            camera_settings
        )

        if not cameras:
            self.report({'WARNING'}, "No cameras were created.")
            return {'CANCELLED'}

        context.scene.camera = cameras[0]

        self.report({'INFO'}, f"Created {len(cameras)} bone cameras")
        return {'FINISHED'}

class VIEW3D_OT_set_active_camera(bpy.types.Operator):
    """Set the active camera and switch to camera view"""
    bl_idname = "view3d.set_active_camera"
    bl_label = "Set Active Camera"
    bl_options = {'REGISTER', 'UNDO'}

    camera_name: bpy.props.StringProperty(name="Camera Name")

    def execute(self, context):
        if self.camera_name in bpy.data.objects:
            camera = bpy.data.objects[self.camera_name]
            if camera.type == 'CAMERA':
                context.scene.camera = camera

                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                space.camera = camera
                                space.region_3d.view_perspective = 'CAMERA'
                                break
                        break

                self.report({'INFO'}, f"Switched to camera {self.camera_name}")
                return {'FINISHED'}

        self.report({'WARNING'}, f"Camera {self.camera_name} not found")
        return {'CANCELLED'}

class VIEW3D_OT_select_all_bones(bpy.types.Operator):
    """Select all bones in the list"""
    bl_idname = "bone_camera.select_all_bones"
    bl_label = "Select All Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for item in context.scene.bone_items:
            item.selected = True
        return {'FINISHED'}

class VIEW3D_OT_select_none_bones(bpy.types.Operator):
    """Deselect all bones in the list"""
    bl_idname = "bone_camera.select_none_bones"
    bl_label = "Deselect All Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for item in context.scene.bone_items:
            item.selected = False
        return {'FINISHED'}

classes = (
    BoneItem,
    BONE_UL_item,
    VIEW3D_PT_bone_cameras,
    VIEW3D_OT_create_bone_cameras,
    VIEW3D_OT_set_active_camera,
    VIEW3D_OT_select_all_bones,
    VIEW3D_OT_select_none_bones
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bone_items = bpy.props.CollectionProperty(type=BoneItem)
    bpy.types.Scene.bone_items_index = bpy.props.IntProperty(default=0)

    bpy.types.Scene.bone_camera_distance = bpy.props.FloatProperty(
        name="Camera Distance",
        description="Camera distance factor relative to bone length",
        default=4.0,
        min=0.1,
        max=20.0
    )

    bpy.types.Scene.bone_camera_type = bpy.props.EnumProperty(
        name="Camera Type",
        description="Type of camera projection",
        items=[
            ('PERSP', "Perspective", "Use perspective projection"),
            ('ORTHO', "Orthographic", "Use orthographic projection")
        ],
        default='PERSP'
    )

    bpy.types.Scene.bone_camera_lens = bpy.props.FloatProperty(
        name="Focal Length",
        description="Focal length in mm for perspective cameras",
        default=35.0,
        min=1.0,
        max=250.0
    )

    bpy.types.Scene.bone_camera_ortho_scale = bpy.props.FloatProperty(
        name="Ortho Scale",
        description="Scale factor for orthographic cameras",
        default=6.0,
        min=0.1,
        max=100.0
    )

    bpy.types.Scene.bone_camera_first_person = bpy.props.BoolProperty(
        name="First-Person View",
        description="Place camera at bone position looking outward (overrides other position settings)",
        default=False,
        update=update_first_person
    )

    bpy.types.Scene.bone_camera_attach_point = bpy.props.EnumProperty(
        name="Attachment Point",
        description="Where to attach the camera on the bone",
        items=[
            ('HEAD', "Head", "Attach to the bone's head (start)"),
            ('TAIL', "Tail", "Attach to the bone's tail (end)"),
            ('MID', "Middle", "Attach to the middle of the bone")
        ],
        default='HEAD'
    )

    bpy.types.Scene.bone_camera_position_type = bpy.props.EnumProperty(
        name="Position Type",
        description="How to position the camera relative to the bone",
        items=[
            ('ANGLED', "Angled", "Position at an angle to the bone (default)"),
            ('RANDOM', "Random", "Position randomly around the bone"),
            ('ALIGNED', "Aligned", "Position along specific axes"),
            ('PERPENDICULAR', "Perpendicular", "Position perpendicular to the bone direction")
        ],
        default='ANGLED',
        update=update_position_type
    )

    bpy.types.Scene.bone_camera_position_axis = bpy.props.EnumProperty(
        name="Alignment Axis",
        description="Which axis or plane to align the camera to",
        items=[
            ('XYZ', "XYZ", "Diagonal in 3D space"),
            ('X', "X", "Along X axis"),
            ('Y', "Y", "Along Y axis"),
            ('Z', "Z", "Along Z axis"),
            ('XY', "XY", "In XY plane"),
            ('XZ', "XZ", "In XZ plane"),
            ('YZ', "YZ", "In YZ plane")
        ],
        default='XYZ'
    )

    bpy.types.Scene.bone_camera_custom_position_enabled = bpy.props.BoolProperty(
        name="Use Custom Position",
        description="Use a custom fixed position for all cameras",
        default=False
    )

    bpy.types.Scene.bone_camera_custom_position = bpy.props.FloatVectorProperty(
        name="Custom Position",
        description="Custom position for all cameras",
        default=(0.0, 0.0, 5.0),
        subtype='TRANSLATION'
    )

    bpy.app.handlers.depsgraph_update_post.append(update_bone_items_handler)

def unregister():

    if update_bone_items_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_bone_items_handler)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bone_items
    del bpy.types.Scene.bone_items_index
    del bpy.types.Scene.bone_camera_distance
    del bpy.types.Scene.bone_camera_type
    del bpy.types.Scene.bone_camera_lens
    del bpy.types.Scene.bone_camera_ortho_scale
    del bpy.types.Scene.bone_camera_first_person
    del bpy.types.Scene.bone_camera_attach_point
    del bpy.types.Scene.bone_camera_position_type
    del bpy.types.Scene.bone_camera_position_axis
    del bpy.types.Scene.bone_camera_custom_position_enabled
    del bpy.types.Scene.bone_camera_custom_position

if __name__ == "__main__":
    register()