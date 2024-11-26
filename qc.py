import bpy
from bpy.app.handlers import persistent
import math
from .bonegenerator import *
from .additive_animation_porter import *
from bpy.props import StringProperty, IntProperty, EnumProperty
from .driver_defs import *
#  C.collection.objects.link(bpy.data.objects["Scout FK Rig.001"])
def add_action_strip(action_name, track_name):
    obj = bpy.context.active_object
    current_frame = bpy.context.scene.frame_current

    # Ensure the object is an armature (or any object with an NLA editor)
    if not obj or not obj.animation_data:
        print("Error: No animation data found on the selected object.")
        return
    
    # Find the action by name
    action = bpy.data.actions.get(action_name)
    if not action:
        print(f"Error: Action '{action_name}' not found.")
        return
    
    # Get the NLA tracks of the object
    nla_tracks = obj.animation_data.nla_tracks

    # Check if the specified track exists; if not, create it
    track = nla_tracks.get(track_name)
    if not track:
        track = nla_tracks.new()
        track.name = track_name

    # Add the action as a new strip on the specified track
    strip = track.strips.new(action_name, start=current_frame, action=action)
    
    # Optional: Set the strip to run in "Hold" mode if you'd like it to hold its final frame
    strip.blend_type = 'REPLACE'  # Default blend mode
    strip.use_auto_blend = True
    strip.extrapolation = 'NOTHING'  # Enables automatic blending with previous/next strips
    
    print(f"Added action strip '{action_name}' to track '{track_name}' starting at frame {current_frame}.")
def add_ik_actions(ik_target, subtarget, b):
    bpy.ops.pose.select_all(action='DESELECT')
    #bpy.context.active_object.pose.bones[subtarget].constraints["IK"].enabled = False
    bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[ik_target].bone
    bpy.context.active_object.pose.bones[ik_target].bone.select = True
    bpy.context.active_object.pose.bones[ik_target].constraints.new('COPY_TRANSFORMS')
    bpy.context.active_object.pose.bones[ik_target].constraints["Copy Transforms"].target = bpy.context.active_object
    bpy.context.active_object.pose.bones[ik_target].constraints["Copy Transforms"].subtarget = subtarget
    bpy.ops.nla.bake(frame_start=0, frame_end=int(bpy.data.actions[b].frame_range[1]), visual_keying=True, clear_constraints=True, use_current_action=True, bake_types={'POSE'})
    #bpy.context.active_object.pose.bones[ik_target].constraints.remove(bpy.context.active_object.pose.bones[ik_target].constraints["Copy Transforms"])
    
               
def setup_ikchain(end_bone, bone_name, ik_name,should_add_ik, **kwargs):
    move =kwargs.get('move', None)
    if bool(bpy.context.active_object.data.edit_bones.get(ik_name)) == False:
        bpy.ops.object.mode_set(mode='EDIT')
        cb = bpy.context.active_object.data.edit_bones.new(ik_name)

        cb.head = bpy.context.active_object.data.edit_bones[end_bone].head
        cb.tail = bpy.context.active_object.data.edit_bones[end_bone].tail
        cb.matrix = bpy.context.active_object.data.edit_bones[end_bone].matrix
        if bone_name != "":
            cb.parent = bpy.context.active_object.data.edit_bones[bone_name]
        bpy.ops.object.mode_set(mode='POSE')
        try:
            bpy.context.active_object.pose.bones[end_bone].constraints.remove(bpy.context.active_object.pose.bones[end_bone].constraints["IK"])
        except KeyError:
            pass
    if should_add_ik:
        bpy.ops.object.mode_set(mode='POSE')
        bpy.context.active_object.pose.bones[end_bone].constraints.new('IK')
        constraint = bpy.context.active_object.pose.bones[end_bone].constraints["IK"] 
        constraint.target = bpy.context.active_object
        constraint.subtarget = ik_name
        constraint.use_rotation = True
        if move:
            constraint.influence = 1
            constraint.chain_count = 3
        else:
            eval = constraint.driver_add("influence")
            constraint.chain_count = 4
            d = eval.driver
            d.type = "SCRIPTED"
            d.expression = "var"
            v = d.variables.new()
            v.name = "var"
            t = v.targets[0]
            t.id_type = 'OBJECT'
            t.id = bpy.data.objects[bpy.context.active_object.name]
            t.data_path = "pose.bones[\"Properties\"][\"radius_look\"]"
def const_create(anim_name, expression, variables, prop_names, suffix_enum, **kwargs):
    only_ik_bone = kwargs.get('only_ik', None)
    should_use_eval = kwargs.get('eval_driver', None)
    for_nla = kwargs.get('for_nla', None)
    prop = anim_name.lower().replace("_" + suffix_enum.lower(), "")
    Prop_holder = bpy.context.active_object.pose.bones["Prop_holder"]
    For_nla_bone = bpy.context.active_object.pose.bones["FOR_NLA"]
    if only_ik_bone == None:
        if bool(Prop_holder.get(prop)) == False:
            Prop_holder[prop] = float(0)
            eval = Prop_holder.driver_add("[\"" + prop + "\"]")
            d = eval.driver
            d.type = "SCRIPTED"
            d.expression = expression
            if "crouch" in prop.lower():
                d.expression = "(" + d.expression + ")*Crouch"
            else:
                d.expression = "(" + d.expression + ")*(1-Crouch)"
            For_nla_bone = bpy.context.active_object.pose.bones["FOR_NLA"]
            if "run" in prop.lower() or "walk" in prop.lower():
                d.expression = "(" + d.expression + ")*radius_move"
            else:
                d.expression = "(" + d.expression + ")*(1-radius_move)"
            for i in variables:
                if i in d.expression:
                    v = d.variables.new()
                    v.name = i
                    t = v.targets[0]
                    t.id_type = 'OBJECT'
                    t.id = bpy.data.objects[bpy.context.active_object.name]
                    t.data_path = "pose.bones[\"Properties\"][\"" + i +"\"]"
        if for_nla == True:
            active_bone = For_nla_bone
            bpy.context.active_object.pose.bones[active_bone.name].constraints.new('ACTION')
            bpy.context.active_object.pose.bones[active_bone.name].constraints["Action"].name = anim_name
            constraint = bpy.context.active_object.pose.bones[active_bone.name].constraints[anim_name]
            constraint.use_eval_time = True
            constraint.action = bpy.data.actions[anim_name]
            constraint.frame_end = int(bpy.data.actions[anim_name].frame_range[1])
        elif for_nla == None:
            for active_bone in bpy.context.active_object.pose.bones:
                if active_bone.name in bpy.context.active_object.data.collections["Base"].bones:
                    bpy.context.active_object.pose.bones[active_bone.name].constraints.new('ACTION')
                    bpy.context.active_object.pose.bones[active_bone.name].constraints["Action"].name = anim_name
                    constraint = bpy.context.active_object.pose.bones[active_bone.name].constraints[anim_name]

                    constraint.action = bpy.data.actions[anim_name]
                    constraint.frame_end = int(bpy.data.actions[anim_name].frame_range[1])
                    if constraint.frame_end == 0:
                        constraint.use_eval_time = True
                    else:
                        constraint.target = bpy.context.active_object
                        if bool(bpy.context.active_object.pose.bones.get(prop)) == False:
                            bpy.ops.object.mode_set(mode='EDIT')
                            bpy.ops.armature.bone_primitive_add(name=prop)
                            bpy.ops.object.mode_set(mode='POSE')
                            subtarget_bone = bpy.context.active_object.pose.bones[prop]
                            bpy.context.active_object.data.collections["DO NOT TOUCH"].assign(subtarget_bone)
                            eval =subtarget_bone.driver_add("location", 0)
                            d = eval.driver
                            d.type = "SCRIPTED"
                            d.expression = "frame %" + str(constraint.frame_end)
                            v = d.variables.new()
                            v.name = prop
                            t = v.targets[0]
                            t.id_type = 'OBJECT'
                            t.id = bpy.data.objects[bpy.context.active_object.name]
                            t.data_path = "pose.bones[\"Prop_holder\"][\"" + prop + "\"]"
                        constraint.subtarget= prop
                        constraint.target_space = 'LOCAL'
                        constraint.max = constraint.frame_end
                        property_manager = Prop_holder.id_properties_ui(prop)
                        property_manager.update(min=constraint.min, max=constraint.max, soft_min=constraint.min, soft_max=constraint.max, step=1)
                    Properties_bone = bpy.context.active_object.pose.bones['Properties']
                    if should_use_eval == None:
                        eval = constraint.driver_add("influence")
                    else:
                        constraint.driver_remove("eval_time")
                        eval = constraint.driver_add("eval_time")
                        Prop_holder.driver_remove("[\"" + prop + "\"]")
                        d = constraint.driver_add("influence").driver
                        d.type="SCRIPTED"
                        d.use_self = True
                        d.expression = "1 if self.eval_time > 0 else 0"
                    d = eval.driver
                    d.type = "SCRIPTED"
                    d.expression = prop
                    for i in variables:
                        if i in constraint.name:
                            v = d.variables.new()
                            v.name = i
                            t = v.targets[0]
                            t.id_type = 'OBJECT'
                            t.id = bpy.data.objects[bpy.context.active_object.name]
                            t.data_path = "pose.bones[\"Properties\"][\"" + i + "\"]"
                    v = d.variables.new()
                    v.name = prop
                    t = v.targets[0]
                    t.id_type = 'OBJECT'
                    t.id = bpy.data.objects[bpy.context.active_object.name]
                    t.data_path = "pose.bones[\"Prop_holder\"][\"" + prop + "\"]"
                    d.expression = "(" + d.expression + ")*" + suffix_enum
                    v = d.variables.new()
                    v.name = suffix_enum
                    t = v.targets[0]
                    t.id_type = 'OBJECT'
                    t.id = bpy.data.objects[bpy.context.active_object.name]
                    t.data_path = "pose.bones[\"Properties\"][\"" + suffix_enum + "\"]"
                    print("added constraint to " + active_bone.name+" for "+constraint.name)
    else:
        bpy.context.active_object.pose.bones["bip_hand_L.001"].constraints.new('ACTION')
        bpy.context.active_object.pose.bones["bip_hand_L.001"].constraints["Action"].name = anim_name
        constraint = bpy.context.active_object.pose.bones["bip_hand_L.001"].constraints[anim_name]
        constraint.use_eval_time = True
        constraint.action = bpy.data.actions[anim_name]
        constraint.frame_end = int(bpy.data.actions[anim_name].frame_range[1])
        for i in bpy.context.active_object.pose.bones["bip_hand_L.001"].constraints:
            #i.driver_remove("influence")
            eval = constraint.driver_add("influence")
            d = eval.driver
            d.type = "SCRIPTED"
            d.expression = expression
            for i in variables:
                if i in d.expression:
                    v = d.variables.new()
                    v.name = i
                    t = v.targets[0]
                    t.id_type = 'OBJECT'
                    t.id = bpy.data.objects[bpy.context.active_object.name]
                    t.data_path = "pose.bones[\"Properties\"][\"" + i + "\"]"
            d.expression = "(" + d.expression + ")*" + suffix_enum
            v = d.variables.new()
            v.name = suffix_enum
            t = v.targets[0]
            t.id_type = 'OBJECT'
            t.id = bpy.data.objects[bpy.context.active_object.name]
            t.data_path = "pose.bones[\"Properties\"][\"" + suffix_enum + "\"]"
            d.expression = d.expression + " if " + expression + " == 0 else " + suffix_enum
    
class BYANON_OT_anim_optimize(bpy.types.Operator):
    bl_idname = 'byanon.optimize'
    bl_label = 'Optimize'
    #bl_description = 'Generate Bones (Properties, AIM, Movement)'
    bl_options = {'UNDO'}

    def execute(self, context):
        object = bpy.context.active_object
        for i in object.pose.bones:
            for ii in i.constraints:
                if ii.type == 'ACTION':
                    ii.enabled = False
        for i in object.animation_data.drivers:
            if ("Properties") in i.data_path:
                pass
            else:
                i.mute = True
        return {'FINISHED'}
class BYANON_OT_anim_unoptimize(bpy.types.Operator):
    bl_idname = 'byanon.unoptimize'
    bl_label = 'Restore'
    #bl_description = 'Generate Bones (Properties, AIM, Movement)'
    bl_options = {'UNDO'}

    def execute(self, context):
        object = bpy.context.active_object
        for i in object.pose.bones:
            for ii in i.constraints:
                if ii.type == 'ACTION':
                    ii.enabled = True
        for b in object.animation_data.drivers:
            if ("Properties") in b.data_path:
                pass
            else:
                b.mute = False
        return {'FINISHED'}
class BYANON_OT_anim_scan(bpy.types.Operator):
    bl_idname = 'byanon.anim_scan'
    bl_label = 'Scan QC'
    
    bl_options = {'UNDO'}
    import_options = []
    def execute(self, context):
        qc = bpy.context.scene.qc_file_path
        folder = qc.removesuffix(".qc") + "_anims"
        file = open(qc, "r")
        buffer = file.readlines()
        file.close()
        list = []
        
        line_index = -1
        for i in buffer:
            line_index +=1
            if ("$sequence \"run_") in i:
                list.append(i.removesuffix("\n"))
                list.append(buffer[line_index + 1].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 2].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 3].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 4].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 5].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 6].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 7].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 8].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 9].removeprefix("	\"").removesuffix("\"\n"))
        for c in list:
            if list.index(c) == 0 or list.index(c) % 10 == 0:
                if c.removeprefix("$sequence \"run_").removesuffix("\" {") not in self.import_options:
                    self.import_options.append(c.removeprefix("$sequence \"run_").removesuffix("\" {"))
                    #BYANON_OT_anim_porter.suffix_enum.append(c.removeprefix("$sequence \"run_").removesuffix("\" {"))
        return {'FINISHED'}
class BYANON_OT_anim_base(bpy.types.Operator):
    bl_idname = 'byanon.base_create'
    bl_label = ''
    #bl_description = 'Generate Bones (Properties, AIM, Movement)'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        bpy.app.driver_namespace["angle"] = angle
        bpy.app.driver_namespace["movement"] = movement
        qc = bpy.context.scene.qc_file_path
        folder = qc.removesuffix(".qc") + "_anims"
        file = open(qc, "r")
        buffer = file.readlines()
        file.close()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.bone_primitive_add(name='Properties')
        bpy.ops.armature.bone_primitive_add(name='Prop_holder')
        bpy.ops.armature.bone_primitive_add(name='FOR_NLA')
        bpy.ops.armature.bone_primitive_add(name='Movement')
        bpy.ops.armature.bone_primitive_add(name='AIM')
        bpy.ops.object.mode_set(mode='POSE')
        prop_names = ["move_x", "move_y", "radius_move", "angle_move", "look_x", "look_y","radius_look", "angle_look", "Crouch", "Stand_Duration", "Crouch_Duration","Run_Duration"]
        variables = ["radius_move", "angle_move","radius_look", "angle_look", "Crouch"]
        Properties_bone = bpy.context.active_object.pose.bones['Properties']
        Props_holder = bpy.context.active_object.pose.bones['Prop_holder']
        For_nla = bpy.context.active_object.pose.bones["FOR_NLA"]
        bpy.context.active_bone.id_data.bones['Prop_holder'].hide = False
        for i in prop_names:
            Properties_bone[i] = float(0)
            Properties_bone.id_properties_ensure()  # Make sure the manager is updated
            property_manager = Properties_bone.id_properties_ui(i)
            if i != "angle_move" and i != "angle_look":
                property_manager.update(min=-1, max=1, soft_min=-1, soft_max=1, step=0.5)
            else:
                property_manager.update(min=-360, max=360, soft_min=-1, soft_max=1, step=0.5)
        
        Movement_bone = bpy.context.active_object.pose.bones['Movement']    
        AIM_bone = bpy.context.active_object.pose.bones['AIM']     
        #radius_move driver    
        eval = Properties_bone.driver_add("[\"radius_move\"]")
        d = eval.driver
        d.type = "SCRIPTED"
        d.expression = "sqrt(move_x*move_x+move_y*move_y) if sqrt(move_x*move_x+move_y*move_y) <= 1 else 1"
        v = d.variables.new()
        v.name = "move_x"
        t = v.targets[0]
        t.id_type = 'OBJECT'
        t.id = bpy.data.objects[bpy.context.active_object.name]
        t.data_path = "pose.bones[\"Properties\"][\"move_x\"]"
        v = d.variables.new()
        v.name = "move_y"
        t = v.targets[0]
        t.id_type = 'OBJECT'
        t.id = bpy.data.objects[bpy.context.active_object.name]
        t.data_path = "pose.bones[\"Properties\"][\"move_y\"]"
        
        #move_x driver    
        eval = Properties_bone.driver_add("[\"move_x\"]")
        d = eval.driver
        d.type = "SCRIPTED"
        d.expression = "-move_x/10"
        v = d.variables.new()
        v.name = "move_x"
        t = v.targets[0]
        t.id_type = 'OBJECT'
        t.id = bpy.data.objects[bpy.context.active_object.name]
        t.data_path = "pose.bones[\"Movement\"].location[0]"
        
        #move_y driver    
        eval = Properties_bone.driver_add("[\"move_y\"]")
        d = eval.driver
        d.type = "SCRIPTED"
        d.expression = "move_y/10"
        v = d.variables.new()
        v.name = "move_y"
        t = v.targets[0]
        t.id_type = 'OBJECT'
        t.id = bpy.data.objects[bpy.context.active_object.name]
        t.data_path = "pose.bones[\"Movement\"].location[2]"
        
        #angle_move driver
        eval = Properties_bone.driver_add("[\"angle_move\"]")
        d = eval.driver
        d.type = "SCRIPTED"
        d.expression = "degrees(atan2(loc[\"move_y\"], loc[\"move_x\"])) if atan2(loc[\"move_y\"], loc[\"move_x\"]) >= 0 else degrees(atan2(loc[\"move_y\"], loc[\"move_x\"])) +360"
        v = d.variables.new()
        v.name = "loc"
        t = v.targets[0]
        t.id_type = 'OBJECT'
        t.id = bpy.data.objects[bpy.context.active_object.name]
        t.data_path = f'pose.bones["{Properties_bone.name}"]'
        
        #radius_look driver    
        eval = Properties_bone.driver_add("[\"radius_look\"]")
        d = eval.driver
        d.type = "SCRIPTED"
        d.expression = "sqrt(look_x*look_x+look_y*look_y) if sqrt(look_x*look_x+look_y*look_y) <= 1 else 1"
        v = d.variables.new()
        v.name = "look_x"
        t = v.targets[0]
        t.id_type = 'OBJECT'
        t.id = bpy.data.objects[bpy.context.active_object.name]
        t.data_path = "pose.bones[\"Properties\"][\"look_x\"]"
        v = d.variables.new()
        v.name = "look_y"
        t = v.targets[0]
        t.id_type = 'OBJECT'
        t.id = bpy.data.objects[bpy.context.active_object.name]
        t.data_path = "pose.bones[\"Properties\"][\"look_y\"]"
        
        #move_x driver    
        eval = Properties_bone.driver_add("[\"look_x\"]")
        d = eval.driver
        d.type = "SCRIPTED"
        d.expression = "look_x/10"
        v = d.variables.new()
        v.name = "look_x"
        t = v.targets[0]
        t.id_type = 'OBJECT'
        t.id = bpy.data.objects[bpy.context.active_object.name]
        t.data_path = "pose.bones[\"AIM\"].location[0]"
        
        #move_y driver    
        eval = Properties_bone.driver_add("[\"look_y\"]")
        d = eval.driver
        d.type = "SCRIPTED"
        d.expression = "-look_y/10"
        v = d.variables.new()
        v.name = "look_y"
        t = v.targets[0]
        t.id_type = 'OBJECT'
        t.id = bpy.data.objects[bpy.context.active_object.name]
        t.data_path = "pose.bones[\"AIM\"].location[1]"
        
        #angle_look driver
        eval = Properties_bone.driver_add("[\"angle_look\"]")
        d = eval.driver
        d.type = "SCRIPTED"
        d.expression = "degrees(atan2(loc[\"look_y\"], loc[\"look_x\"])) if atan2(loc[\"look_y\"], loc[\"look_x\"]) >= 0 else degrees(atan2(loc[\"look_y\"], loc[\"look_x\"])) +360"
        v = d.variables.new()
        v.name = "loc"
        t = v.targets[0]
        t.id_type = 'OBJECT'
        t.id = bpy.data.objects[bpy.context.active_object.name]
        t.data_path = f'pose.bones["{Properties_bone.name}"]'
        

                

        Movement_bone.constraints.new('LIMIT_LOCATION')
        Movement_bone.constraints["Limit Location"].use_min_x = True
        Movement_bone.constraints["Limit Location"].use_min_y = True
        Movement_bone.constraints["Limit Location"].use_min_z = True

        Movement_bone.constraints["Limit Location"].use_max_x = True
        Movement_bone.constraints["Limit Location"].use_max_y = True
        Movement_bone.constraints["Limit Location"].use_max_z = True

        Movement_bone.constraints["Limit Location"].min_x = -10
        Movement_bone.constraints["Limit Location"].min_y = 0
        Movement_bone.constraints["Limit Location"].min_z = -10

        Movement_bone.constraints["Limit Location"].max_x = 10
        Movement_bone.constraints["Limit Location"].max_y = 0
        Movement_bone.constraints["Limit Location"].max_z = 10
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
        AIM_bone.constraints["Limit Location"].min_z = -0

        AIM_bone.constraints["Limit Location"].max_x = 10
        AIM_bone.constraints["Limit Location"].max_y = 10
        AIM_bone.constraints["Limit Location"].max_z = 0
        AIM_bone.constraints["Limit Location"].use_transform_limit = True
        AIM_bone.constraints["Limit Location"].owner_space = 'LOCAL'
        bpy.context.active_object.data.collections[0].name = "Base"
        bpy.context.active_object.data.collections.new(name="Controls")
        bpy.context.active_object.data.collections.new(name="DO NOT TOUCH")
        bpy.context.active_object.data.collections["Controls"].assign(AIM_bone)
        bpy.context.active_object.data.collections["Controls"].assign(Movement_bone)
        bpy.context.active_object.data.collections["DO NOT TOUCH"].assign(Properties_bone)
        bpy.context.active_object.data.collections["DO NOT TOUCH"].assign(Props_holder)
        bpy.context.active_object.data.collections["DO NOT TOUCH"].assign(For_nla)
        bpy.context.active_object.data.collections["DO NOT TOUCH"].is_visible = False
        return {'FINISHED'}
class BYANON_OT_anim_port(bpy.types.Operator):
    bl_idname = 'byanon.anim_port'
    bl_label = 'Port SMD Anims'
    #bl_description = 'Generate Bones (Properties, AIM, Movement)'
    bl_options = {'UNDO'}
    suffix_enum : StringProperty()
    def execute(self, context):
        bpy.app.driver_namespace["angle"] = angle
        bpy.app.driver_namespace["movement"] = movement
        qc = bpy.context.scene.qc_file_path
        folder = qc.removesuffix(".qc") + "_anims"
        file = open(qc, "r")
        buffer = file.readlines()
        file.close()
        bpy.ops.object.mode_set(mode='POSE')
        prop_names = ["move_x", "move_y", "radius_move", "angle_move", "look_x", "look_y","radius_look", "angle_look", "Crouch", "Stand_Duration", "Crouch_Duration","Run_Duration"]
        variables = ["move_x", "move_y", "radius_move", "angle_move", "look_x", "look_y","radius_look", "angle_look", "Crouch"]
        import_options =[]
        if bpy.context.active_object.pose.bones["bip_hand_L"].constraints.get("IK") == None:
            setup_ikchain("bip_hand_L", "weapon_bone", "bip_hand_L.001", should_add_ik=True)
        if bpy.context.active_object.pose.bones["bip_foot_L"].constraints.get("IK") == None:
            setup_ikchain("bip_foot_L", "", "bip_foot_L.001", move=True, should_add_ik=False)
        bpy.context.active_object.data.collections["Base"].assign(bpy.context.active_object.pose.bones["bip_foot_L.001"])
        if bpy.context.active_object.pose.bones["bip_foot_R"].constraints.get("IK") == None:
            setup_ikchain("bip_foot_R", "", "bip_foot_R.001", move=True, should_add_ik=False)
        bpy.context.active_object.data.collections["Base"].assign(bpy.context.active_object.pose.bones["bip_foot_R.001"])
        Properties_bone = bpy.context.active_object.pose.bones['Properties']
        list = []
        line_index = -1
        for i in buffer:
            line_index +=1
            if ("$sequence \"run_") in i:
                list.append(i.removesuffix("\n"))
                list.append(buffer[line_index + 1].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 2].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 3].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 4].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 5].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 6].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 7].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 8].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 9].removeprefix("	\"").removesuffix("\"\n"))

        # bpy.ops.object.mode_set(mode='EDIT')
        # bpy.context.active_object.data.edit_bones['bip_pelvis'].parent= bpy.context.active_object.data.edit_bones['Movement_Parent']        
        # bpy.ops.object.mode_set(mode='POSE')
        
        Properties_bone[self.suffix_enum] = float(0)
        Properties_bone.id_properties_ensure()  # Make sure the manager is updated
        property_manager = Properties_bone.id_properties_ui(self.suffix_enum)
        property_manager.update(min=0, max=1, soft_min=0, soft_max=1, step=0.5)

        list = []
        line_index = -1
        for i in buffer:
            line_index +=1
            if ("$sequence \""+self.suffix_enum+"_aimmatrix") in i:
                list.append(i.removesuffix("\n"))
                list.append(buffer[line_index + 4].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 5].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 6].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 7].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 8].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 9].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 10].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 11].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 12].removeprefix("	\"").removesuffix("\"\n"))

        for b in list:
            if list.index(b) != 0 and list.index(b) % 10 != 0 and self.suffix_enum in b:
                ANON_OT_load_additive.filepath = folder + "/" + b + ".smd"
                create_action(b)
                ANON_OT_load_additive.execute(ANON_OT_load_additive, context)
                print("ported add anim " + b)
                #animation_correct(list, b)
                ANON_OT_load_additive.filepath = folder
                #bpy.context.active_object.animation_data.action = None
        for b in list:
            if list.index(b) != 0 and list.index(b) % 10 != 0 and self.suffix_enum in b:
                n = list.index(b) % 10
                match n:
                    case 1:
                        const_create(b, "radius_look*((1-abs(angle_look-225)/45) if abs(angle_look-225)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 2:
                        const_create(b, "radius_look*((1-abs(angle_look-270)/45) if abs(angle_look-270)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 3:
                        const_create(b, "radius_look*((1-abs(angle_look-315)/45) if abs(angle_look-315)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 4:
                        const_create(b, "radius_look*((1-abs(angle_look-180)/45) if abs(angle_look-180)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 5:
                        const_create(b, "1-radius_look", variables, prop_names, self.suffix_enum)
                    case 6:
                        const_create(b, "radius_look*((1-abs(angle_look-(0 if angle_look < 315 else 360))/45) if abs(angle_look-(0 if angle_look < 315 else 360))<=45 else 0)", variables, prop_names, self.suffix_enum) #need adjusting
                    case 7:
                        const_create(b, "radius_look*((1-abs(angle_look-135)/45) if abs(angle_look-135)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 8:
                        const_create(b, "radius_look*((1-abs(angle_look-90)/45) if abs(angle_look-90)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 9:
                        const_create(b, "radius_look*((1-abs(angle_look-45)/45) if abs(angle_look-45)<=45 else 0)", variables, prop_names, self.suffix_enum)
        for b in buffer:            
            print(b)            
            if (self.suffix_enum.lower()+"_" in b.lower() or self.suffix_enum.lower()+"\"" in b.lower() ) and "@" not in b and "layer" not in b and "$sequence" in b and "aim" not in b:
                b1 = buffer.index(b)         
                for i in range(b1, len(buffer)+1):
                    if buffer[i] == "}\n":
                        b2 = i
                        break
                for i in range(b1, b2):
                    if "delta" in buffer[i]:
                        b =b.removesuffix("\" {\n").removeprefix("$sequence \"").removesuffix("/")
                        print(b)
                        ANON_OT_load_additive.filepath = folder + "/" + b + ".smd"
                        create_action(b)                                
                        ANON_OT_load_additive.execute(ANON_OT_load_additive, context)
                        print("ported add anim " + b)
                        ANON_OT_load_additive.filepath = folder
                        const_create(b, "Crouch",variables,prop_names, self.suffix_enum, for_nla = True)
                        break        
        list = []
        line_index = -1
        for i in buffer:
            line_index +=1
            if ("$sequence \"run_") + self.suffix_enum + "\" {" in i:
                list.append(i.removesuffix("\n"))
                list.append(buffer[line_index + 1].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 2].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 3].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 4].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 5].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 6].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 7].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 8].removeprefix("	\"").removesuffix("\"\n"))
                list.append(buffer[line_index + 9].removeprefix("	\"").removesuffix("\"\n"))
        for b in list:
            if list.index(b) != 0 and list.index(b) % 10 != 0 and self.suffix_enum in b:
                bpy.ops.import_scene.smd(filepath = folder + "/" + b + ".smd", rotMode = 'QUATERNION')
                animation_correct(list, b)
                bpy.context.scene.frame_set(0)
                add_ik_actions("bip_foot_L.001", "bip_foot_L", b)
                add_ik_actions("bip_foot_R.001", "bip_foot_R", b)
        bpy.ops.import_scene.smd(filepath = folder + "/" + "stand_" + self.suffix_enum + ".smd", rotMode = 'QUATERNION')
        bpy.context.scene.frame_set(0)
        bpy.ops.object.mode_set(mode='POSE')
        add_ik_actions("bip_foot_L.001", "bip_foot_L", "stand_" + self.suffix_enum)
        add_ik_actions("bip_foot_R.001", "bip_foot_R", "stand_" + self.suffix_enum)
        #bpy.context.active_object.pose.bones["bip_foot_L"].constraints["IK"].enabled = True
        #bpy.context.active_object.pose.bones["bip_foot_R"].constraints["IK"].enabled = False
        for b in list:
            if list.index(b) != 0 and list.index(b) % 10 != 0:        
                n = list.index(b) % 10
                match n:
                    case 1:
                        const_create(b, "((1-abs(angle_move-225)/45) if abs(angle_move-225)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 2:
                        const_create(b, "((1-abs(angle_move-270)/45) if abs(angle_move-270)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 3:
                        const_create(b, "((1-abs(angle_move-315)/45) if abs(angle_move-315)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 4:
                        const_create(b, "((1-abs(angle_move-180)/45) if abs(angle_move-180)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 5:
                        const_create("stand_" + self.suffix_enum, "1-radius_move", variables, prop_names, self.suffix_enum)
                    case 6:
                        const_create(b, "((1-abs(angle_move-(0 if angle_move < 315 else 360))/45) if abs(angle_move-(0 if angle_move < 315 else 360))<=45 else 0)", variables, prop_names, self.suffix_enum) #need adjusting
                    case 7:
                        const_create(b, "((1-abs(angle_move-135)/45) if abs(angle_move-135)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 8:
                        const_create(b, "((1-abs(angle_move-90)/45) if abs(angle_move-90)<=45 else 0)", variables, prop_names, self.suffix_enum)
                    case 9:
                        const_create(b, "((1-abs(angle_move-45)/45) if abs(angle_move-45)<=45 else 0)", variables, prop_names, self.suffix_enum)
        bpy.data.actions.new("IK_" + self.suffix_enum)
        bpy.context.active_object.animation_data.action = bpy.data.actions["IK_" + self.suffix_enum]
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()
        Properties_bone[self.suffix_enum] = 1.0
        bpy.context.scene.frame_set(0)
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones["bip_hand_L.001"].bone
        bpy.context.active_object.pose.bones["bip_hand_L.001"].bone.select = True
        bpy.context.active_object.pose.bones["bip_hand_L.001"].constraints.new('COPY_TRANSFORMS')
        bpy.context.active_object.pose.bones["bip_hand_L.001"].constraints["Copy Transforms"].target = bpy.context.active_object
        bpy.context.active_object.pose.bones["bip_hand_L.001"].constraints["Copy Transforms"].subtarget = "bip_hand_L"
        bpy.ops.constraint.apply(constraint="Copy Transforms", owner='BONE')
        bpy.context.active_object.pose.bones["bip_hand_L.001"].keyframe_insert(data_path="location", frame = 0)
        bpy.context.active_object.pose.bones["bip_hand_L.001"].keyframe_insert(data_path="rotation_quaternion", frame = 0)
        bpy.context.active_object.animation_data.action = None
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()
        if bpy.context.active_object.pose.bones["bip_foot_L"].constraints.get("IK") == None:
            setup_ikchain("bip_foot_L", "", "bip_foot_L.001", move=True, should_add_ik=True)
        bpy.context.active_object.data.collections["Base"].unassign(bpy.context.active_object.pose.bones["bip_foot_L.001"])
        if bpy.context.active_object.pose.bones["bip_foot_R"].constraints.get("IK") == None:
            setup_ikchain("bip_foot_R", "", "bip_foot_R.001", move=True, should_add_ik=True)
        const_create("IK_" + self.suffix_enum, "radius_look", variables, prop_names, self.suffix_enum, only_ik = True)
        bpy.context.active_object.data.collections["Base"].unassign(bpy.context.active_object.pose.bones["bip_foot_R.001"])
        bpy.context.active_object.data.collections["DO NOT TOUCH"].assign(bpy.context.active_object.pose.bones["bip_foot_L.001"])
        bpy.context.active_object.data.collections["DO NOT TOUCH"].assign(bpy.context.active_object.pose.bones["bip_hand_L.001"])
        if bpy.data.actions.get("Config") == None:
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.loc_clear()
            bpy.ops.pose.rot_clear()
            Properties_bone["Run_Duration"] = 0.0
            Properties_bone.keyframe_insert(data_path = '["Run_Duration"]', frame = 0)
            Properties_bone["Run_Duration"] = 1.0
            Properties_bone.keyframe_insert(data_path = '["Run_Duration"]', frame = bpy.data.actions["a_runNE_"+self.suffix_enum].frame_end)
            Properties_bone["Stand_Duration"] = 0.0
            Properties_bone.keyframe_insert(data_path = '["Stand_Duration"]', frame = 0)
            Properties_bone["Stand_Duration"] = 1.0
            Properties_bone.keyframe_insert(data_path = '["Stand_Duration"]', frame = bpy.data.actions["stand_" + self.suffix_enum].frame_end)
            bpy.context.active_object.animation_data.action.name = "Config"
        else:
            bpy.context.active_object.animation_data.action = bpy.data.actions["Config"]
        Properties_bone[self.suffix_enum] = 0.0
        bpy.context.active_object.data.collections["DO NOT TOUCH"].assign(bpy.context.active_object.pose.bones["bip_foot_L.001"])
        bpy.context.active_object.data.collections["DO NOT TOUCH"].assign(bpy.context.active_object.pose.bones["bip_hand_L.001"])
        return {'FINISHED'}
    
class BYANON_PT_anim_parent(bpy.types.Panel):
    bl_label = "TF2 Game Rig Manager"
    bl_category = "TF2 Game Rig Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "qc_file_path", text="Select TXT File")

class BYANON_PT_anim_porter(bpy.types.Panel):
    bl_label = ''
    bl_category = "TF2 Game Rig Manager"
    bl_space_type = "VIEW_3D"
    bl_parent_id = "BYANON_PT_anim_parent"
    bl_region_type = "UI"
    def draw_header(self, context):
        self.layout.separator()
        self.layout.label(text='SET-UP')
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator('byanon.anim_scan')
        layout.operator('byanon.base_create', text="Create base")
        for i in BYANON_OT_anim_scan.import_options:
            if BYANON_OT_anim_scan.import_options.index(i) == 0:
                self.layout.label(text='Weapons')
                box = layout.box()
            box.operator('byanon.anim_port', text="Import " + i).suffix_enum = i

class BYANON_PT_anim_manager(bpy.types.Panel):
    bl_label = ''
    bl_category = "TF2 Game Rig Manager"
    bl_space_type = "VIEW_3D"
    bl_parent_id = "BYANON_PT_anim_parent"
    bl_region_type = "UI"
    def draw_header(self, context):
        self.layout.separator()
        self.layout.label(text='MANAGER')
    def draw(self, context):
        layout = self.layout  
        scene = context.scene
        actionlist = scene.action_list      
        # Display the custom properties in a UI list
        layout.template_list("BYANON_UL_CustomPropsList", "", context.scene, "custom_props_collection", context.scene, "custom_props_collection_index")
        layout.prop(actionlist, "actions_enum")
        layout.operator("byanon.strip_add")
# Operator to update custom properties list
class BYANON_OT_strip_add(bpy.types.Operator):
    bl_idname = "byanon.strip_add"
    bl_label = "Add Action"

    
    def execute(self, context):
        scene = context.scene
        actionlist = scene.action_list
        add_action_strip(action_name=actionlist.actions_enum, track_name="Add Anims")
        return {'FINISHED'}

# Define a UI List to display custom properties
class BYANON_UL_CustomPropsList(bpy.types.UIList):
    def filter_items(self, context, data, propname):
        #props = context.scene.hisanimvars
        items = getattr(data, propname)
        filtered = [self.bitflag_filter_item] * len(items)
        for i, item in enumerate(items):
            if self.filter_name.lower() not in item.name.lower():
                filtered[i] &= ~self.bitflag_filter_item
            
            find = f'pose.bones["Prop_holder"]["{item.name}"]'
            if context.object.animation_data.drivers.find(find) != None:
                filtered[i] &= ~self.bitflag_filter_item
            find = f'pose.bones["Properties"]["{item.name}"]'
            if context.object.animation_data.drivers.find(find) != None:
                filtered[i] &= ~self.bitflag_filter_item
            if "Duration" in item.name:
                filtered[i] &= ~self.bitflag_filter_item
        return filtered, []
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = context.object
        bone_name = "Properties"

        if obj and obj.type == 'ARMATURE' and bone_name in obj.pose.bones:
            bone = obj.pose.bones[bone_name]

            # Retrieve the actual custom property value by its name
            if item.name in bone.keys():
                row = layout.row()
                
                # Directly display the property as a slider
                row.prop(bone, f'["{item.name}"]', text=item.name, slider= True)
@persistent
def update_custom_props_collection(scn = None):
    obj = bpy.context.object
    bone_name = "Properties"
    props = bpy.context.scene.custom_props_collection
    if obj and obj.type == 'ARMATURE' and bone_name in obj.pose.bones:
        bone = obj.pose.bones[bone_name]
        
        # Clear the collection and populate it with the bone's custom properties
        custom_props_collection = bpy.context.scene.custom_props_collection
        custom_props_collection.clear()
        
        for key in bone.keys():
            if not key.startswith("_"):  # Skip internal properties
                item = custom_props_collection.add()
                item.name = key
                value = bone[key]
                
                # Dynamically set the value based on type
                if isinstance(value, float):
                    item.value = value
                elif isinstance(value, int):
                    item.value = float(value)  # Convert int to float for slider
                else:
                    item.value = 0.0  # Default for unsupported types
def update_action_list(context):
    obj = bpy.context.object
    bone_name = "FOR_NLA"
    items = bpy.context.scene.dynamic_action_items
    if obj and obj.type == 'ARMATURE' and bone_name in obj.pose.bones:
        bone = obj.pose.bones[bone_name]
        
        # Clear the collection and populate it with the bone's custom properties
        for key in bone.constraints:
            if key.type == 'ACTION':  # Skip internal properties
                return[ (key.name, key.name, f"Constraint: {key.name}")]
                '''value = bone[key]
                
                # Dynamically set the value based on type
                if isinstance(value, float):
                    item.value = value
                elif isinstance(value, int):
                    item.value = float(value)  # Convert int to float for slider
                else:
                    item.value = 0.0  # Default for unsupported types'''
def get_enum_items(self, context):
    # Return an empty list if no items are defined yet
    obj = bpy.context.object
    bone_name = "FOR_NLA"
    items = bpy.context.scene.dynamic_action_items
    if obj and obj.type == 'ARMATURE' and bone_name in obj.pose.bones:
        bone = obj.pose.bones[bone_name]
        
        # Clear the collection and populate it with the bone's custom properties
        return[ (key.name, key.name, f"Constraint: {key.name}") for key in bone.constraints if key.type == 'ACTION']
    else:
        return[]
    

# Custom property item for UI list display
class CustomPropertyItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    value: bpy.props.FloatProperty()
class ActionGroups(bpy.types.PropertyGroup):
    actions_enum : bpy.props.EnumProperty(
        name="Enumerator / Dropdown",
        description="action list",
        items=get_enum_items
    )
class BYANON_OT_nla_adder(bpy.types.Operator):
    pass
classes = [BYANON_PT_anim_parent, BYANON_OT_anim_port, BYANON_OT_anim_optimize, BYANON_OT_anim_unoptimize, BYANON_OT_anim_scan, BYANON_OT_anim_base, BYANON_PT_anim_porter, BYANON_PT_anim_manager, CustomPropertyItem,
    BYANON_UL_CustomPropsList, ActionGroups, BYANON_OT_strip_add]
def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.Scene.qc_file_path = StringProperty(
        name="QC File Path",
        default="C:/Program Files (x86)/Steam/steamapps/common/tf_misc_dir/root/models/player/Anims/HEAVY/heavy_animations.qc"
        #default="/data/data/com.termux/files/home/storage/shared/BLENDER ANIMATIONS DECOMPLIE/SOLDIER/Demo_Animations//soldier_animations.qc"
    )
    bpy.types.Scene.custom_props_collection = bpy.props.CollectionProperty(type=CustomPropertyItem)
    bpy.types.Scene.custom_props_collection_index = bpy.props.IntProperty()
    bpy.types.Scene.action_list = bpy.props.PointerProperty(type=ActionGroups)
    bpy.types.Scene.dynamic_action_items = []
    bpy.app.handlers.depsgraph_update_post.append(update_custom_props_collection)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
    del bpy.types.Scene.qc_file_path
    del bpy.types.Scene.anim_folder_path
    del bpy.types.Scene.custom_props_collection
    del bpy.types.Scene.custom_props_collection_index
    del bpy.types.Scene.action_list
    del bpy.types.Scene.dynamic_action_items
    bpy.app.handlers.depsgraph_update_post.remove(update_custom_props_collection)