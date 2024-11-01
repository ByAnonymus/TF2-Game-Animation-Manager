import bpy
import math
from .bonegenerator import *
from .additive_animation_porter import *
from bpy.props import StringProperty, IntProperty, EnumProperty
from .driver_defs import *
def setup_ikchain(end_bone, bone_name, ik_name):
    bpy.ops.object.mode_set(mode='EDIT')
    cb = bpy.context.active_object.data.edit_bones.new(ik_name)

    cb.head = bpy.context.active_object.data.edit_bones[end_bone].tail
    cb.tail = bpy.context.active_object.data.edit_bones[end_bone].head
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
    prop = anim_name.replace("_" + suffix_enum, "")
    Prop_holder = bpy.context.active_object.pose.bones["Prop_holder"]
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
                    t.data_path = "pose.bones[\"Properties\"][\"" + i + "\"]"
        for active_bone in bpy.context.active_object.pose.bones:
            if (active_bone.name not in ["Properties", "Movement", "rootTransform", "AIM", "Prop_holder", "bip_hand_L.001"]):
            
                bpy.context.active_object.pose.bones[active_bone.name].constraints.new('ACTION')
                bpy.context.active_object.pose.bones[active_bone.name].constraints["Action"].name = anim_name
                constraint = bpy.context.active_object.pose.bones[active_bone.name].constraints[anim_name]
                constraint.use_eval_time = True
                constraint.action = bpy.data.actions[anim_name]
                constraint.frame_end = int(bpy.data.actions[anim_name].frame_range[1])

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
                    '''Properties_bone["Stand_Duration"] = 0.0
                    Properties_bone.keyframe_insert(data_path = '["Stand_Duration"]', frame = 0)
                    #print("done")
                    Properties_bone["Stand_Duration"] = 1.0
                    Properties_bone.keyframe_insert(data_path = '["Stand_Duration"]', frame = constraint.frame_end)'''
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
                if "run" in constraint.name:
                    t.data_path = "pose.bones[\"Properties\"][\"Run_Duration\"]"

                eval = constraint.driver_add("influence")
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
        bpy.ops.armature.bone_primitive_add(name='Movement')
        bpy.ops.armature.bone_primitive_add(name='AIM')
        bpy.ops.object.mode_set(mode='POSE')
        prop_names = ["move_x", "move_y", "radius_move", "angle_move", "look_x", "look_y","radius_look", "angle_look", "Crouch", "Stand_Duration", "Crouch_Duration","Run_Duration"]
        variables = ["radius_move", "angle_move","radius_look", "angle_look", "Crouch"]
        Properties_bone = bpy.context.active_object.pose.bones['Properties']
        bpy.context.active_bone.id_data.bones['Prop_holder'].hide = True
        
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
        Movement_bone.constraints["Limit Location"].min_y = -10
        Movement_bone.constraints["Limit Location"].min_z = -10

        Movement_bone.constraints["Limit Location"].max_x = 10
        Movement_bone.constraints["Limit Location"].max_y = 10
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
        variables = ["radius_move", "angle_move","radius_look", "angle_look", "Crouch"]
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
                        const_create(b, "radius_look*movement(angle_look, 180, 270, False)", variables, prop_names, self.suffix_enum)
                    case 2:
                        const_create(b, "radius_look*movement(angle_look, 225, 315, False)", variables, prop_names, self.suffix_enum)
                    case 3:
                        const_create(b, "radius_look*movement(angle_look, 270, 360, False)", variables, prop_names, self.suffix_enum)
                    case 4:
                        const_create(b, "radius_look*movement(angle_look, 135, 225, False)", variables, prop_names, self.suffix_enum)
                    case 5:
                        const_create(b, "1-radius_look", variables, prop_names, self.suffix_enum)
                    case 6:
                        const_create(b, "radius_look*movement(angle_look, 315, 45, True)", variables, prop_names, self.suffix_enum)
                    case 7:
                        const_create(b, "radius_look*movement(angle_look, 90, 180, False)", variables, prop_names, self.suffix_enum)
                    case 8:
                        const_create(b, "radius_look*movement(angle_look, 45, 135, False)", variables, prop_names, self.suffix_enum)
                    case 9:
                        const_create(b, "radius_look*movement(angle_look, 0, 90, False)", variables, prop_names, self.suffix_enum)
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

        for b in list:
            if list.index(b) != 0 and list.index(b) % 10 != 0 and self.suffix_enum in b:
                bpy.ops.import_scene.smd(filepath = folder + "/" + b + ".smd", rotMode = 'QUATERNION')
                animation_correct(list, b)
        bpy.ops.import_scene.smd(filepath = folder + "/" + "stand_" + self.suffix_enum + ".smd", rotMode = 'QUATERNION')
        for b in list:
            if list.index(b) != 0 and list.index(b) % 10 != 0 and self.suffix_enum in b:        
                n = list.index(b) % 10
                match n:
                    case 1:
                        const_create(b, "radius_move*movement(angle_move, 180, 270, False)", variables, prop_names, self.suffix_enum)
                    case 2:
                        const_create(b, "radius_move*movement(angle_move, 225, 315, False)", variables, prop_names, self.suffix_enum)
                    case 3:
                        const_create(b, "radius_move*movement(angle_move, 270, 360, False)", variables, prop_names, self.suffix_enum)
                    case 4:
                        const_create(b, "radius_move*movement(angle_move, 135, 225, False)", variables, prop_names, self.suffix_enum)
                    case 5:
                        const_create("stand_"+self.suffix_enum, "1-radius_move", variables, prop_names, self.suffix_enum)
                    case 6:
                        const_create(b, "radius_move*movement(angle_move, 315, 45, True)", variables, prop_names, self.suffix_enum)
                    case 7:
                        const_create(b, "radius_move*movement(angle_move, 90, 180, False)", variables, prop_names, self.suffix_enum)
                    case 8:
                        const_create(b, "radius_move*movement(angle_move, 45, 135, False)", variables, prop_names, self.suffix_enum)
                    case 9:
                        const_create(b, "radius_move*movement(angle_move, 0, 90, False)", variables, prop_names, self.suffix_enum)
            print("added driver {b}")
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
            Properties_bone.keyframe_insert(data_path = '["Run_Duration"]', frame = bpy.context.active_object.pose.bones["bip_pelvis"].constraints["a_runNE_"+self.suffix_enum].frame_end)
            Properties_bone["Stand_Duration"] = 0.0
            Properties_bone.keyframe_insert(data_path = '["Stand_Duration"]', frame = 0)
            Properties_bone["Stand_Duration"] = 1.0
            Properties_bone.keyframe_insert(data_path = '["Stand_Duration"]', frame = bpy.context.active_object.pose.bones["bip_pelvis"].constraints["stand_" + self.suffix_enum].frame_end)
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
        scene = context.scene
        layout.operator('byanon.anim_scan')

classes = [BYANON_PT_anim_parent, BYANON_OT_anim_port, BYANON_OT_anim_optimize, BYANON_OT_anim_unoptimize, BYANON_OT_anim_scan, BYANON_OT_anim_base, BYANON_PT_anim_porter, BYANON_PT_anim_manager, ]
def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.Scene.qc_file_path = StringProperty(
        name="TXT File Path",
        default="C:/Program Files (x86)/Steam/steamapps/common/tf_misc_dir/root/models/player/Anims/Soldier/soldier_animations.qc"
    )
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
    del bpy.types.Scene.qc_file_path
    del bpy.types.Scene.anim_folder_path