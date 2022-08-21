from tiny_seq_tools_master.line_art_tools.core import (
    sync_line_art_obj_to_strip,
)
from tiny_seq_tools_master.line_art_tools.line_art_cam.core import (
    get_line_art_from_scene,  ## Exists because of LINEARTCAMBUG
)
import bpy


class lr_seq_items(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    mod_name: bpy.props.StringProperty()

    def get_thickness(self):
        obj = self.object
        if obj.type == "GPENCIL":
            return obj.grease_pencil_modifiers[self.mod_name].thickness
        return 0

    def set_thickness(self, thickness: int):

        frame = self.id_data.sequence_editor.active_strip.frame_final_start
        if frame > self.id_data.sequence_editor.active_strip.scene.frame_current_final:
            return
        if self.id_data.objects is None:
            return 0
        obj = self.object
        line_art_mod = [
            mod for mod in obj.grease_pencil_modifiers if mod.type == "GP_LINEART"
        ]
        fcurves = obj.animation_data.action.fcurves
        keyframes = fcurves[0].keyframe_points
        for mod in line_art_mod:
            mod.thickness = thickness
            mod.keyframe_insert("thickness", frame=frame)

        for key in keyframes:
            if key.co[0] in range(
                frame, self.id_data.sequence_editor.active_strip.frame_final_end
            ):
                if key.co[0] == frame:
                    key.co[1] = thickness
                if key.co[0] in range(
                    frame + 1, self.id_data.sequence_editor.active_strip.frame_final_end
                ):
                    for mod in line_art_mod:
                        mod.keyframe_delete("thickness", frame=key.co[0])

        return

    def get_status(self):
        scene = self.id_data
        strip = scene.sequence_editor.active_strip
        return sync_line_art_obj_to_strip(self.object, strip)

    def get_viewport(self):
        for modifier in self.object.grease_pencil_modifiers:
            if modifier.type == "GP_LINEART":
                return modifier.show_viewport

    def set_viewport(self, val: bool):
        for modifier in self.object.grease_pencil_modifiers:
            if modifier.type == "GP_LINEART":
                modifier.show_viewport = val

    status: bpy.props.BoolProperty(
        name="Keyframe Sync Status",
        get=get_status,
        description="Line Art keyframes are out of sync with the sequencer, please update by adjusting the thickness to update keyframes or adjust manually.",
    )
    thickness: bpy.props.IntProperty(
        name="Line Art Seq",
        default=0,
        get=get_thickness,
        set=set_thickness,
        options=set(),
    )
    viewport: bpy.props.BoolProperty(
        name="Viewport Display Seq Line Art",
        get=get_viewport,
        set=set_viewport,
        options=set(),
        description="Hide and Show Line Art Modifiers in Viewports",
    )


def get_line_art_seq_cam_state(self):
    obj = self
    if obj.grease_pencil_modifiers is None:
        return False
    for mod in obj.grease_pencil_modifiers:
        if mod.type == "GP_LINEART":
            return True
    return False


def set_line_art_seq_cam_state(self, value: bool):
    obj = self
    for mod in obj.grease_pencil_modifiers:
        if mod.type == "GP_LINEART":
            return True
    return False


classes = (lr_seq_items,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.line_art_list = bpy.props.CollectionProperty(type=lr_seq_items)
    bpy.types.Scene.line_art_cam_override = (
        bpy.types.Object.line_art_seq_cam
    ) = bpy.props.BoolProperty(
        name="Override Camera",
        description="Render Line Art from the Tiny Line Art camera (which needs to be refreshed)",
        default=False,
    )
    bpy.types.Object.line_art_seq_cam = bpy.props.BoolProperty(
        name="Enable Seq Line Art Control",
        default=False,
        get=get_line_art_seq_cam_state,
        set=set_line_art_seq_cam_state,
        options=set(),
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
