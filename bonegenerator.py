import bpy, json, os
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
import math
from bpy.props import *
from .additive_animation_porter import *


def folder_import(self, context, parent):
    filename, extension = os.path.splitext(parent.filepath)
    with open(parent.filepath,'r') as dictionary: 
        anim_dict = json.load(dictionary)
    folder = "C:/Program Files (x86)/Steam/steamapps/common/Team Fortress 2/tf_misc_dir/root/models/player/Anims/SNIPER/sniper_animations_anims/"
    bpy.ops.object.mode_set(mode='POSE')
    for i in anim_dict.keys():
        ii = anim_dict[i]
        self.filepath = folder + ii + ".smd"
        if ("AIM" or "gesture") in i:
            try:
                ANON_OT_load_additive.execute(self, context)
                bpy.context.active_object.animation_data.action.name = ii
            except FileNotFoundError:
                continue
        else:
            try:
                #AnonSmdImporter.execute(self, context)
                pass
            except FileNotFoundError:
                continue
            try:
                if "walk" in bpy.context.active_object.animation_data.action.name or "run" in bpy.context.active_object.animation_data.action.name:
                    continue
                    #animation_correct(parent)
            except AttributeError:
                continue
        bpy.context.active_object.animation_data.action = None
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()


    bpy.data.actions.new('Config')
    bpy.context.active_object.animation_data.action = bpy.data.actions["Config"]





def add_constraint(self, anim_folder):
    filename, extension = os.path.splitext(self.filepath)
    with open(self.filepath,'r') as dictionary: 
        anim_dict = json.load(dictionary)
    with open(self.const_dict_path,'r') as dictionary: 
        const_dict = json.load(dictionary)
    
    for i in anim_dict.keys():
        if bpy.data.actions.get(anim_dict[i]) != None:
            for active_bone in bpy.context.active_object.pose.bones:
                if (active_bone.name not in ["Properties", "Movement", "rootTransform", "AIM"]) : #or (bpy.context.active_object.pose.bones["FaceControls"] not in active_bone.parent_recursive)
                
                    bpy.context.active_object.pose.bones[active_bone.name].constraints.new('ACTION')
                    bpy.context.active_object.pose.bones[active_bone.name].constraints["Action"].name = i
                    constraint = bpy.context.active_object.pose.bones[active_bone.name].constraints[i]
                    constraint.use_eval_time = True
                    constraint.action = bpy.data.actions[anim_dict[i]]
    
                    constraint.frame_end = int(bpy.data.actions[anim_dict[i]].frame_range[1])
                    
                    Properties_bone = bpy.context.active_object.pose.bones['Properties']
    
    
    
                    eval = constraint.driver_add("eval_time")
                    d = eval.driver
                    d.type = "SCRIPTED"
                    d.expression = "Duration"
    
                    v = d.variables.new()
                    v.name = "Duration"
                    t = v.targets[0]
                    t.id_type = 'OBJECT'
                    t.id = bpy.data.objects[bpy.context.active_object.name]
                    if "stand" in constraint.name:
                        t.data_path = "pose.bones[\"Properties\"][\"Stand_Duration\"]"
                        Properties_bone["Stand_Duration"] = 0.0
                        Properties_bone.keyframe_insert(data_path = '["Stand_Duration"]', frame = 0)
                        #print("done")
                        Properties_bone["Stand_Duration"] = 1.0
                        Properties_bone.keyframe_insert(data_path = '["Stand_Duration"]', frame = constraint.frame_end)
                    elif "Crouch" in constraint.name:
                        t.data_path = "pose.bones[\"Properties\"][\"Crouch_Duration\"]"
                        Properties_bone["Crouch_Duration"] = 0.0
                        Properties_bone.keyframe_insert(data_path = '["Crouch_Duration"]', frame = 0)
                        #print("done")
                        Properties_bone["Crouch_Duration"] = 1.0
                        Properties_bone.keyframe_insert(data_path = '["Crouch_Duration"]', frame = constraint.frame_end)
                    elif "CrouchWalk" in constraint.name:
                        t.data_path = "pose.bones[\"Properties\"][\"CrouchWalk_Duration\"]"
                        Properties_bone["CrouchWalk_Duration"] = 0.0
                        Properties_bone.keyframe_insert(data_path = '["CrouchWalk_Duration"]', frame = 0)
                        #print("done")
                        Properties_bone["CrouchWalk_Duration"] = 1.0
                        Properties_bone.keyframe_insert(data_path = '["CrouchWalk_Duration"]', frame = constraint.frame_end)
                    elif "Run" in constraint.name:
                        t.data_path = "pose.bones[\"Properties\"][\"Run_Duration\"]"
                        Properties_bone["Run_Duration"] = 0.0
                        Properties_bone.keyframe_insert(data_path = '["Run_Duration"]', frame = 0)
                        #print("done")
                        Properties_bone["Run_Duration"] = 1.0
                        Properties_bone.keyframe_insert(data_path = '["Run_Duration"]', frame = constraint.frame_end)
                
                Properties_bone = bpy.context.active_object.pose.bones['Properties']
                
                for a in const_dict.keys():
                    if active_bone.name not in ["Properties", "Movement", "rootTransform", "AIM"]:
                        if a in active_bone.constraints[i].name:
                            influence = active_bone.constraints[i].driver_add("influence")
                            d = influence.driver
                            d.type = "SCRIPTED"
                            d.expression = const_dict[a]
    
                            if "AIM" not in active_bone.constraints[i].name:
                                v = d.variables.new()
                                v.name = "locationY"
    
                                t = v.targets[0]
                                t.id_type = 'OBJECT'
                                t.id = bpy.data.objects[bpy.context.active_object.name]
                                t.data_path = "pose.bones[\"Movement\"].location[1]"
    
                                v = d.variables.new()
                                v.name = "locationX"
    
                                t = v.targets[0]
                                t.id_type = 'OBJECT'
                                t.id = bpy.data.objects[bpy.context.active_object.name]
                                t.data_path = "pose.bones[\"Movement\"].location[0]"
    
    
                                v = d.variables.new()
                                v.name = "locationZ"
    
                                t = v.targets[0]
                                t.id_type = 'OBJECT'
                                t.id = bpy.data.objects[bpy.context.active_object.name]
                                t.data_path = "pose.bones[\"Movement\"].location[2]"
    
                                for b in self.class_ident:
                                    if b in active_bone.constraints[i].name:
                                        d.expression = "(" + d.expression + ")*" + b
                                        v = d.variables.new()
                                        v.name = b
                                        t = v.targets[0]
                                        t.id_type = 'OBJECT'
                                        t.id = bpy.data.objects[bpy.context.active_object.name]
                                        t.data_path = "pose.bones[\"Properties\"]" + "[\"" + b + "\"]"
    
                            else:
                                v = d.variables.new()
                                v.name = "locationY"
    
                                t = v.targets[0]
                                t.id_type = 'OBJECT'
                                t.id = bpy.data.objects[bpy.context.active_object.name]
                                t.data_path = "pose.bones[\"AIM\"].location[1]"
    
                                v = d.variables.new()
                                v.name = "locationX"
    
                                t = v.targets[0]
                                t.id_type = 'OBJECT'
                                t.id = bpy.data.objects[bpy.context.active_object.name]
                                t.data_path = "pose.bones[\"AIM\"].location[0]"
    
    
                                v = d.variables.new()
                                v.name = "locationZ"
    
                                t = v.targets[0]
                                t.id_type = 'OBJECT'
                                t.id = bpy.data.objects[bpy.context.active_object.name]
                                t.data_path = "pose.bones[\"AIM\"].location[2]"
    
                                for b in self.class_ident:
                                    if b in active_bone.constraints[i].name:
                                        d.expression = "(" + d.expression + ")*" + b
                                        v = d.variables.new()
                                        v.name = b
                                        t = v.targets[0]
                                        t.id_type = 'OBJECT'
                                        t.id = bpy.data.objects[bpy.context.active_object.name]
                                        t.data_path = "pose.bones[\"Properties\"]" + "[\"" + b + "\"]"
                            
def animation_correct(list, b):
    bpy.context.scene.frame_set(0)
    bpy.ops.object.mode_set(mode='POSE')
    active_bone = bpy.context.active_object.id_data.pose.bones["bip_pelvis"]
    bpy.ops.pose.select_all(action='DESELECT')
    active_bone.bone.select = True
    bpy.ops.view3d.snap_cursor_to_selected()
    print(bpy.context.scene.cursor.location)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.empty_add()
    bpy.context.view_layer.objects.active = bpy.data.objects["Empty"]
    bpy.data.objects["Empty"].location = bpy.context.scene.cursor.location
    for i in range(0, int(bpy.data.actions[active_bone.id_data.animation_data.action.name].frame_range[1])):
        bpy.context.scene.frame_set(i)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = active_bone.id_data
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.view3d.snap_cursor_to_selected()
        
        active_bone.bone.select = True
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects["Empty"]
        if list.index(b) != 0 and list.index(b) % 10 != 0 and "PRIMARY" in b:        
            n = list.index(b) % 10
            match n:
                case 1 | 3 | 7|9:
                    bpy.data.objects["Empty"].location[2] = bpy.context.scene.cursor.location[2]
                case 2|8:
                    bpy.data.objects["Empty"].location[0] = bpy.context.scene.cursor.location[0]
                    bpy.data.objects["Empty"].location[2] = bpy.context.scene.cursor.location[2]
                case 4|6:
                    bpy.data.objects["Empty"].location[1] = bpy.context.scene.cursor.location[1]
                    bpy.data.objects["Empty"].location[2] = bpy.context.scene.cursor.location[2]
            print("cursor = ", bpy.context.scene.cursor.location, "empty = ", bpy.data.objects["Empty"].location)
        bpy.data.objects["Empty"].keyframe_insert(data_path = "location", frame = i)
        bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = active_bone.id_data
    bpy.ops.object.mode_set(mode='POSE')    
    active_bone.constraints.new('COPY_LOCATION')
    active_bone.constraints["Copy Location"].target = bpy.data.objects["Empty"]


    bpy.ops.nla.bake(frame_start=0, frame_end=int(bpy.data.actions[active_bone.id_data.animation_data.action.name].frame_range[1]), visual_keying=True, clear_constraints=False, use_current_action=True, bake_types={'POSE'})
    active_bone.constraints.remove(active_bone.constraints["Copy Location"])
    bpy.data.actions.remove(bpy.data.objects["Empty"].animation_data.action)
    bpy.data.objects.remove(bpy.data.objects["Empty"])




class BYANON_OT_bone_generator(bpy.types.Operator):
    bl_idname = 'byanon.bone_generator'
    bl_label = 'Generate Control Bones'
    bl_description = 'Generate Bones (Properties, AIM, Movement)'
    bl_options = {'UNDO'}
    filepath = "G:/My Drive/Scripts/addons/AnimDict.json"
    const_dict_path = "G:/My Drive/Scripts/addons/ConstraintDict.json"
    anim_folder = ""
    class_ident = ["ITEM1", "PRIMARY", "SECONDARY", "MELEE", "MELEE_ALLCLASS"]
    pelvis_bone = "bip_pelvis"
    speed = 0.0

    prop_names = ["AIM_CENTER_DOWN", "AIM_CENTER_LEFT", "AIM_CENTER_RIGHT", "AIM_CENTER_UP", "CrouchWalk_Duration", "Crouch_Duration", "Stand_Duration", "Run_Duration", "ITEM1", "PRIMARY", "SECONDARY", "MELEE", "MELEE_ALLCLASS"]

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object.pose.bones != None
    def execute(self, context):
        # our code goes here
        current_armature = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.bone_primitive_add(name='Properties')
        bpy.ops.armature.bone_primitive_add(name='Movement')
        bpy.ops.armature.bone_primitive_add(name='AIM')
        bpy.ops.object.mode_set(mode='POSE')
        Properties_bone = current_armature.pose.bones['Properties']
        Movement_bone = current_armature.pose.bones['Movement']
        AIM_bone = current_armature.pose.bones['AIM']

        Movement_bone.constraints.new('LIMIT_LOCATION')
        Movement_bone.constraints["Limit Location"].use_min_x = True
        Movement_bone.constraints["Limit Location"].use_min_y = True
        Movement_bone.constraints["Limit Location"].use_min_z = True

        Movement_bone.constraints["Limit Location"].use_max_x = True
        Movement_bone.constraints["Limit Location"].use_max_y = True
        Movement_bone.constraints["Limit Location"].use_max_z = True

        Movement_bone.constraints["Limit Location"].min_x = -10
        Movement_bone.constraints["Limit Location"].min_y = -10
        Movement_bone.constraints["Limit Location"].min_z = 0

        Movement_bone.constraints["Limit Location"].max_x = 10
        Movement_bone.constraints["Limit Location"].max_y = 10
        Movement_bone.constraints["Limit Location"].max_z = 0
        Movement_bone.constraints["Limit Location"].use_transform_limit = True
        Movement_bone.constraints["Limit Location"].owner_space = 'LOCAL'

        AIM_bone.constraints.new('LIMIT_LOCATION')
        AIM_bone.constraints["Limit Location"].use_min_x = True
        AIM_bone.constraints["Limit Location"].use_min_y = True
        AIM_bone.constraints["Limit Location"].use_min_z = True

        AIM_bone.constraints["Limit Location"].use_max_x = True
        AIM_bone.constraints["Limit Location"].use_max_y = True
        AIM_bone.constraints["Limit Location"].use_max_z = True

        AIM_bone.constraints["Limit Location"].min_x = -10
        AIM_bone.constraints["Limit Location"].min_y = -10
        AIM_bone.constraints["Limit Location"].min_z = 0

        AIM_bone.constraints["Limit Location"].max_x = 10
        AIM_bone.constraints["Limit Location"].max_y = 10
        AIM_bone.constraints["Limit Location"].max_z = 0
        AIM_bone.constraints["Limit Location"].use_transform_limit = True
        AIM_bone.constraints["Limit Location"].owner_space = 'LOCAL'

        Movement_bone.rotation_mode = 'XYZ'
        Movement_bone.rotation_euler.x = math.radians(90)


        bpy.ops.pose.select_all(action='DESELECT')
        current_armature.data.bones['Movement'].select = True

        bpy.ops.pose.armature_apply(selected=True)

        
        
        for i in self.prop_names:
            Properties_bone[i] = float(0)
            Properties_bone.id_properties_ensure()  # Make sure the manager is updated
            property_manager = Properties_bone.id_properties_ui(i)
            property_manager.update(min=0, max=1, soft_min=0, soft_max=1, step=0.5)


        #folder_import(AnonSmdImporter, context, self)


        add_constraint(self, self.anim_folder)        

        for fc in bpy.data.actions['Config'].fcurves:
            for k in fc.keyframe_points:
                k.interpolation = 'LINEAR'
                k.handle_left_type = 'VECTOR'
                k.handle_right_type = 'VECTOR'
        bpy.ops.pose.select_all(action='DESELECT')
        Properties_bone.bone.select = True
        bpy.ops.action.extrapolation_type = "MAKE_CYCLIC"

        return {'FINISHED'}

classes = [BYANON_OT_bone_generator]

def register():
    for i in classes:
        bpy.utils.register_class(i)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)