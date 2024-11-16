from math import radians
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import *

D = bpy.data
def create_action(anim_name):
    bpy.context.active_object.animation_data.action = None
    bpy.data.actions.new(anim_name)
    bpy.context.active_object.animation_data.action = bpy.data.actions[anim_name]
class ANON_OT_load_additive(Operator, ImportHelper):
    bl_idname = 'tf2.loadadditive'
    bl_label = 'Load Additive Animation'
    bl_options = {'UNDO'}
    
    filepath: StringProperty()
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        #armature = bpy.context.object.data.name
        smd = open(self.filepath, 'r')
        file = smd.readlines()
        dict = {}
        blist = []

        for line in file:
            line = line.strip()
            if line == "end":
                break
            try:
                var = int(line[0])
            except:
                continue
            cleanup = line.replace('"', "")
            info = cleanup.split(" ")
            blist.append(info[0])
            dict[info[0]] = info[1]

        skeleswitch = 0
        
        
        
        for line in file:
            if skeleswitch == 0:
                if line.strip() == "skeleton":
                    skeleswitch = 1
                continue
            line = line.strip()
            if line.startswith("end"):
                break

            if line.startswith("time"):
                line = line.split(" ")
                bpy.context.scene.frame_set(int(line[1]))
                continue
            line = line.split(" ")

            try:
                bone = bpy.context.object.pose.bones[dict[line[0]]]
                x, y, z = float(line[1]), float(line[2]), float(line[3])

                rx, ry, rz = float(line[4]), float(line[5]), float(line[6])
                bone.rotation_mode = "XYZ" # must be set or else rotations aren't keyframed
                bone.rotation_euler[0] = rx
                bone.rotation_euler[1] = ry
                bone.rotation_euler[2] = rz 
                if bone.name == "bip_pelvis":
                    bone.rotation_euler[2] += radians(90)
                bone.rotation_mode = 'QUATERNION'
                bone.keyframe_insert(data_path="rotation_quaternion")
            except KeyError:
                # file list bones which are not in the armature, we ignore those
                pass
        smd.close()
        return {'FINISHED'}
    
bpy.utils.register_class(ANON_OT_load_additive)