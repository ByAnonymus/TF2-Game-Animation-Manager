import bpy
import math
from .bonegenerator import *
from .additive_animation_porter import *
from bpy.props import StringProperty, IntProperty, EnumProperty
from .driver_defs import *
def setup_ikchain(end_bone, bone_name, ik_name):
    bpy.ops.object.mode_set(mode='EDIT')
    cb = bpy.context.active_object.data.edit_bones.new(ik_name)

    cb.head = bpy.context.active_object.data.edit_bones[end_bone].head
    cb.tail = bpy.context.active_object.data.edit_bones[end_bone].tail
    cb.matrix = bpy.context.active_object.data.edit_bones[end_bone].matrix
    cb.parent = bpy.context.active_object.data.edit_bones[bone_name]
    bpy.ops.object.mode_set(mode='POSE')
    bpy.context.active_object.pose.bones[end_bone].constraints.new('IK')
    constraint = bpy.context.active_object.pose.bones[end_bone].constraints["IK"]
    constraint.target = bpy.context.active_object
    constraint.subtarget = ik_name
    constraint.use_rotation = True
    constraint.chain_count = 3
    eval = constraint.driver_add("influence")
    d = eval.driver
    d.type = "SCRIPTED"
    d.expression = "radius_look"
    v = d.variables.new()
    v.name = "radius_look"
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
                            d.expression = prop
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
                    if "crouch" in constraint.name.lower():
                        d.expression = "(" + d.expression + ")*Crouch"
                    else:
                        d.expression = "(" + d.expression + ")*(1-Crouch)"
                    v = d.variables.new()
                    v.name = suffix_enum
                    t = v.targets[0]
                    t.id_type = 'OBJECT'
                    t.id = bpy.data.objects[bpy.context.active_object.name]
                    t.data_path = "pose.bones[\"Properties\"][\"" + suffix_enum + "\"]"
                    v = d.variables.new()
                    v.name = "Crouch"
                    t = v.targets[0]
                    t.id_type = 'OBJECT'
                    t.id = bpy.data.objects[bpy.context.active_object.name]
                    t.data_path = "pose.bones[\"Properties\"][\"Crouch\"]"
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
        d.expression = "angle(move_x, move_y)"
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
        
        #angle_move driver
        eval = Properties_bone.driver_add("[\"angle_look\"]")
        d = eval.driver
        d.type = "SCRIPTED"
        d.expression = "angle(look_x, look_y)"
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

        
        Movement_bone = bpy.context.active_object.pose.bones['Movement']            

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
        
        AIM_bone = bpy.context.active_object.pose.bones['AIM']            

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
            setup_ikchain("bip_hand_L", "weapon_bone", "bip_hand_L.001")
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
            if ("$sequence \"") in i and ("aimmatrix") in i and ("run") in i and ("crouch") not in i and ("runS") not in i:
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
                        const_create(b, "1-sqrt((-1-look_x)**2+(-1-look_y)**2)", variables, prop_names, self.suffix_enum)
                    case 2:
                        const_create(b, "1-sqrt((0-look_x)**2+(-1-look_y)**2)", variables, prop_names, self.suffix_enum)
                    case 3:
                        const_create(b, "1-sqrt((1-look_x)**2+(-1-look_y)**2)", variables, prop_names, self.suffix_enum)
                    case 4:
                        const_create(b, "1-sqrt((-1-look_x)**2+(0-look_y)**2)", variables, prop_names, self.suffix_enum)
                    case 5:
                        const_create(b, "1-sqrt((0-look_x)**2+(0-look_y)**2)", variables, prop_names, self.suffix_enum)
                    case 6:
                        const_create(b, "1-sqrt((1-look_x)**2+(0-look_y)**2)", variables, prop_names, self.suffix_enum)
                    case 7:
                        const_create(b, "1-sqrt((-1-look_x)**2+(1-look_y)**2)", variables, prop_names, self.suffix_enum)
                    case 8:
                        const_create(b, "1-sqrt((0-look_x)**2+(1-look_y)**2)", variables, prop_names, self.suffix_enum)
                    case 9:
                        const_create(b, "1-sqrt((1-look_x)**2+(1-look_y)**2)", variables, prop_names, self.suffix_enum)
        for b in buffer:            
            print(b)            
            if (self.suffix_enum.lower()+"_" in b.lower() or self.suffix_enum.lower()+"\"" in b.lower() ) and "@" not in b and "layer" not in b and "$sequence" in b and "aim" not in b and "swim" not in b.lower() and "crouch" not in b.lower():
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
        bpy.ops.import_scene.smd(filepath = folder + "/" + "stand_" + self.suffix_enum + ".smd", rotMode = 'QUATERNION')
        for b in list:
            if list.index(b) != 0 and list.index(b) % 10 != 0:        
                n = list.index(b) % 10
                match n:
                    case 1: const_create(b, "1-sqrt((-1-move_x)**2+(-1-move_y)**2)", variables, prop_names, self.suffix_enum)
                    case 2: const_create(b, "1-sqrt((0-move_x)**2+(-1-move_y)**2)", variables, prop_names, self.suffix_enum)
                    case 3: const_create(b, "1-sqrt((1-move_x)**2+(-1-move_y)**2)", variables, prop_names, self.suffix_enum)
                    case 4: const_create(b, "1-sqrt((-1-move_x)**2+(0-move_y)**2)", variables, prop_names, self.suffix_enum)
                    case 5: const_create("stand_" + self.suffix_enum, "1-sqrt((0-move_x)**2+(0-move_y)**2)", variables, prop_names, self.suffix_enum)
                    case 6: const_create(b, "1-sqrt((1-move_x)**2+(0-move_y)**2)", variables, prop_names, self.suffix_enum)
                    case 7: const_create(b, "1-sqrt((-1-move_x)**2+(1-move_y)**2)", variables, prop_names, self.suffix_enum)
                    case 8: const_create(b, "1-sqrt((0-move_x)**2+(1-move_y)**2)", variables, prop_names, self.suffix_enum)
                    case 9: const_create(b, "1-sqrt((1-move_x)**2+(1-move_y)**2)", variables, prop_names, self.suffix_enum)
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
        const_create("IK_" + self.suffix_enum, "radius_look", variables, prop_names, self.suffix_enum, only_ik = True)
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
        layout.operator("object.update_custom_props", text="Refresh Custom Properties")
        
        # Display the custom properties in a UI list
        layout.template_list("BYANON_UL_CustomPropsList", "", context.scene, "custom_props_collection", context.scene, "custom_props_collection_index")
# Operator to update custom properties list
class BYANON_OT_UpdateCustomProps(bpy.types.Operator):
    bl_idname = "object.update_custom_props"
    bl_label = "Update Custom Properties"

    def execute(self, context):
        obj = context.object
        bone_name = "Properties"
        bone_name2 = "Prop_holder"

        if obj and obj.type == 'ARMATURE' and bone_name in obj.pose.bones:
            # Clear any existing property UI items
            context.scene.custom_props_collection.clear()

            bone = obj.pose.bones[bone_name]
            bone2 = obj.pose.bones[bone_name2]
            for key in bone.keys():
                if not key.startswith("_"):  # Skip internal properties
                    item = context.scene.custom_props_collection.add()
                    item.name = key
                    item.value = key  # Store the property key instead of its value
            for key in bone2.keys():
                if not key.startswith("_"):  # Skip internal properties
                    item = context.scene.custom_props_collection.add()
                    item.name = key
                    item.value = key  # Store the property key instead of its value
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
        bone_name2 = "Prop_holder"

        if obj and obj.type == 'ARMATURE' and bone_name in obj.pose.bones:
            bone = obj.pose.bones[bone_name]
            bone2 = obj.pose.bones[bone_name2]

            # Retrieve the actual custom property value by its name
            if item.name in bone.keys():
                row = layout.row()
                
                # Directly display the property as a slider
                row.prop(bone, f'["{item.name}"]', text=item.name, slider=True)
            if item.name in bone2.keys():
                row = layout.row()
                
                # Directly display the property as a slider
                row.prop(bone2, f'["{item.name}"]', text=item.name, slider=True)
# Custom property item for UI list display
class CustomPropertyItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    value: bpy.props.StringProperty()

classes = [BYANON_PT_anim_parent, BYANON_OT_anim_port, BYANON_OT_anim_optimize, BYANON_OT_anim_unoptimize, BYANON_OT_anim_scan, BYANON_OT_anim_base, BYANON_PT_anim_porter, BYANON_PT_anim_manager, CustomPropertyItem,
    BYANON_OT_UpdateCustomProps,
    BYANON_UL_CustomPropsList,]
def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.Scene.qc_file_path = StringProperty(
        name="TXT File Path",
        default="C:/Program Files (x86)/Steam/steamapps/common/tf_misc_dir/root/models/player/Anims/PYRO/pyro_animations.qc"
        #default="/data/data/com.termux/files/home/storage/shared/BLENDER ANIMATIONS DECOMPLIE/SOLDIER/Demo_Animations//soldier_animations.qc"
    )
    bpy.types.Scene.custom_props_collection = bpy.props.CollectionProperty(type=CustomPropertyItem)
    bpy.types.Scene.custom_props_collection_index = bpy.props.IntProperty()
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
    del bpy.types.Scene.qc_file_path
    del bpy.types.Scene.anim_folder_path
bpy.types.PoseBone