from unittest import skip
from tiny_seq_tools_master.line_art_tools.core import (
    sync_line_art_obj_to_strip,
    get_object_animation_is_constant,
)


import bpy


class SEQUENCER_OT_add_line_art_obj(bpy.types.Operator):
    bl_idname = "view3d.add_line_art_obj"
    bl_label = "add_line_art_obj"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.active_object
            and context.active_object.type == "GPENCIL"
            and not context.active_object.line_art_seq_cam
        )

    def execute(self, context):
        obj = context.active_object
        line_art_items = context.scene.line_art_list
        for index, item in enumerate(line_art_items):
            if item.object == obj:
                line_art_items.remove(index)
        new_mod = False
        if not any(
            [mod for mod in obj.grease_pencil_modifiers if mod.type == "GP_LINEART"]
        ):
            obj.grease_pencil_modifiers.new(name="Line Art", type="GP_LINEART")
            new_mod = True
        for modifier in obj.grease_pencil_modifiers:
            if modifier.type == "GP_LINEART":
                modifier.target_layer = obj.data.layers[0].info
                modifier.target_material = obj.data.materials[0]
                modifier.use_custom_camera = True
                add_line_art_item = line_art_items.add()
                add_line_art_item.object = obj
                add_line_art_item.mod_name = modifier.name
                if new_mod:
                    modifier.source_type = "SCENE"

        line_art_mod = obj.grease_pencil_modifiers["Line Art"]

        for strip in context.scene.sequence_editor.sequences_all:
            line_art_mod.keyframe_insert("thickness", frame=strip.frame_final_start)

        for fcurve in line_art_mod.id_data.original.animation_data.action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = "CONSTANT"

        obj.line_art_seq_cam = True
        self.report({"INFO"}, f"Added '{obj.name}' to Sequence_Line Art Items")
        return {"FINISHED"}


class SEQUENCER_OT_remove_line_art_obj(bpy.types.Operator):
    bl_idname = "view3d.remove_line_art_obj"
    bl_label = "remove_line_art_obj"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (
            context.active_object
            and context.active_object.type == "GPENCIL"
            and context.active_object.line_art_seq_cam
        )

    def execute(self, context):
        obj = context.active_object
        # Remove from list of line_art_items
        for item in context.scene.line_art_list:
            line_art_items = context.scene.line_art_list
        for index, item in enumerate(context.scene.line_art_list):
            if item.object == obj:
                line_art_items.remove(index)
        for mod in obj.grease_pencil_modifiers:
            if mod.type == "GP_LINEART":
                obj.grease_pencil_modifiers.remove(mod)
        self.report({"INFO"}, f"Removed '{obj.name}' from Sequence_Line Art Items")
        return {"FINISHED"}


class SEQUENCER_OT_refresh_line_art_obj(bpy.types.Operator):
    bl_idname = "view3d.refresh_line_art_obj"
    bl_label = "refresh_line_art_obj"

    def execute(self, context):
        strip = context.active_sequence_strip
        if not strip or strip.type != "SCENE":
            self.report({"ERROR"}, "There is no active scene strip")
            return {"CANCELLED"}

        line_art_items = context.scene.line_art_list
        line_art_items.clear()
        for obj in strip.scene.objects:
            if obj.line_art_seq_cam:
                add_line_art_item = line_art_items.add()
                add_line_art_item.object = obj
                add_line_art_item.mod_name = obj.grease_pencil_modifiers[0].name
        self.report({"INFO"}, "Line Art List Updated")
        return {"FINISHED"}


class SEQUENCER_OT_check_line_art_obj(bpy.types.Operator):
    bl_idname = "view3d.check_line_art_obj"
    bl_label = "check_line_art_obj"

    def execute(self, context):
        error_msg = ""
        for item in context.scene.line_art_list:
            obj = item.object
            constant_anim = get_object_animation_is_constant(obj)
            if constant_anim:
                for strip in context.scene.sequence_editor.sequences_all:
                    if strip.type == "SCENE":
                        if not sync_line_art_obj_to_strip(obj, strip):
                            error_msg += f"Object: '{obj.name}' unexpected keyframes within Frame Range: ({strip.frame_final_start}-{strip.frame_final_end}) \n"
            if not constant_anim:
                error_msg += f"UNKOWN ERROR in Object: '{obj.name}' usually caused by wrong interpolation type or missing keyframe error \n"
        if error_msg != "":
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}
        self.report({"INFO"}, "All Line Art Objects Good")
        return {"FINISHED"}


classes = (
    SEQUENCER_OT_add_line_art_obj,
    SEQUENCER_OT_remove_line_art_obj,
    SEQUENCER_OT_refresh_line_art_obj,
    SEQUENCER_OT_check_line_art_obj,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
