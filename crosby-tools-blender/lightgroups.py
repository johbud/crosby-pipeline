import bpy
from bpy.types import Operator
from .helpers import ShowMessageBox


class CROSBY_OT_lightgroups(Operator):
    bl_label = "Add lightgroups"
    bl_idname = "addonname.myop_lightgroups"
    bl_description = "Add lightgroups for selected lights."

    def execute(self, context):
        lightlist = []

        for obj in bpy.context.selected_objects:
            if obj.type == "LIGHT":
                obj.lightgroup = obj.name
                lightlist.append(obj)

        if len(lightlist) < 1:
            message = "No lights selected."
            ShowMessageBox(message=message)
            return {"CANCELLED"}

        bpy.context.scene.world.lightgroup = "L_HDRI"

        bpy.ops.scene.view_layer_add_used_lightgroups()
        bpy.ops.scene.view_layer_remove_unused_lightgroups()

        message = "Lightgroups set."
        ShowMessageBox(message=message)

        return {"FINISHED"}
