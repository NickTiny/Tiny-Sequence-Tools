import bpy

from tiny_seq_tools_master.core_functions.label import split_lines
from tiny_seq_tools_master.rig_tools.rig_editor.core import check_modifier_and_constraint_viewport


class SEQUENCER_PT_rig_settings(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "SEQUENCER_PT_rig_settings"
    bl_label = "Rig Settings"
    bl_category = "Tiny Rig Edit"

    bpy.types.Scene.obj_selection = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.bone_selection = bpy.props.StringProperty()

    def draw(self, context):
        layout = self.layout
        layout.operator("rigools.create_2d_armature")
        layout.prop(context.scene, "target_armature" )
        obj = context.scene.target_armature
        if obj is not None and obj.type == "ARMATURE" :
            self.layout.prop_search(
                    context.scene, "bone_selection", obj.id_data.pose, "bones", text="Property Bone"
                )
        layout.operator("rigools.initialize_rig")
        if obj is None or not obj.tiny_rig.is_rig:
            self.layout.label(text="Rig not Found", icon="ARMATURE_DATA")
            return
        layout.label(text=f"Turnaround Length: {obj.tiny_rig.pose_length}")        


class SEQUENCER_PT_turnaround_editor(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "SEQUENCER_PT_turnaround_editor"
    bl_label = "Turnaround Editor"
    bl_category = "Tiny Rig Edit"

    def draw(self, context):
        obj = context.scene.target_armature
        if obj is None:
            self.layout.label(text="'Target Armature' not set", icon="ARMATURE_DATA")
            return
        if obj is None or not(obj.tiny_rig.is_rig and obj.tiny_rig.is_turnaround):
            self.layout.label(text="Rig has no turnaround", icon="ARMATURE_DATA")
            return
        offset_row = self.layout.row(align=True)
        layout = self.layout.box()
        message_row = layout.row()
        
        

        action_row = layout.row(align=True)
        
        editor_active = not(context.window_manager.offset_editor_active)
        action_row.enabled = editor_active
        action_row.prop(obj, "offset_action")

        action_row.operator("rigools.load_action", icon="FILE_REFRESH", text="")
        
        offset_row.operator("rigools.enable_offset_action", icon="ACTION_TWEAK", depress=not(editor_active)).enable = editor_active
        if (
            context.window_manager.offset_editor_active
            and context.active_object.mode != "POSE"
        ):  
            
            message_row.alert = True
            message_row.label(icon="ERROR",text="Offset Editor is still Active")
        layout.operator("rigools.add_action_const_to_bone", icon="CONSTRAINT_BONE")
        
        
class SEQUENCER_PT_rig_grease_pencil(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "SEQUENCER_PT_rig_grease_pencil"
    bl_label = "Rig Grease Pencil"
    bl_category = "Tiny Rig Edit"

    def draw(self, context):
        if context.active_object.type == "GPENCIL":
            status = check_modifier_and_constraint_viewport(context.active_object)
            context.window_manager.gpencil_editor = context.active_object
            box = self.layout.box()
            box_row = box.row(align=True)
            obj_row = box_row.split(factor=.5, align=True)
            obj_row.prop(
                context.window_manager, "gpencil_editor", text="", icon="OUTLINER_OB_GREASEPENCIL"
            )
            obj_row.enabled = True
            obj_row.operator("rigools.enable_gp_mod_const", text="", icon=("HIDE_OFF" if status else "HIDE_ON"), depress=status).enabled = not(status)
        else:
            warn_row = self.layout.box()
            warn_row.label(
                text=f"Active Object is not Grease Pencil", icon="INFO"
            )
        self.layout.operator("rigools.enable_all_gp_mod_const_all", icon="HIDE_OFF")
        layout = self.layout
        col = layout.column(align=True)
        col.operator("rigools.gp_constraint_armature", icon="CONSTRAINT")
        col.operator("rigools.gp_vertex_by_layer",
                     icon="OUTLINER_DATA_GP_LAYER")
        col.operator("rigools.gp_rig_via_lattice", icon="MOD_LATTICE")
        layout.operator(
            "rigtools.gp_add_time_offset_with_driver", icon="MOD_TIME")
        



class SEQUENCER_PT_rig_properties(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "SEQUENCER_PT_rig_properties"
    bl_label = "Rig Properties"
    bl_category = "Tiny Rig Edit"
    bl_parent_id = "SEQUENCER_PT_rig_settings"

    def draw(self, context):    
        obj = context.scene.target_armature
        self.layout.operator("rigools.add_custom_prop", icon="PLUS")
        self.layout.separator()

        # Time Offset Properties
        time_offset_props = self.layout.box()
        self.layout.separator
        time_offset_props.label(text="User Properties", icon="USER")


        self.layout.separator()
        # All Properties
        prop_col = self.layout.box()
        prop_col.label(text="Other Properties", icon="OUTLINER_OB_ARMATURE")   

        if obj is None:
            return
        try:
            if obj.type != "ARMATURE":
                return
            prop_bone = obj.pose.bones[context.scene.bone_selection]
            
            if len(prop_bone.keys()) == 0:
                prop_col.label(text = f"No Properties on '{prop_bone.name}'")
            for x in [x for x in prop_bone.keys() if x in obj.tiny_rig.user_props]:
                time_offset_props.prop(prop_bone, f'["{x}"]') 
            for x in [x for x in prop_bone.keys() if x not in obj.tiny_rig.user_props]:
                prop_col.prop(prop_bone, f'["{x}"]') 
            
        except KeyError or AttributeError:
            prop_col.label(text = "No Property Bone Found")
            return
        

        



classes = (
    SEQUENCER_PT_rig_settings,
    SEQUENCER_PT_turnaround_editor,
    SEQUENCER_PT_rig_properties,
    SEQUENCER_PT_rig_grease_pencil,
)


def register():
    for i in classes:
        bpy.utils.register_class(i)


def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
