
import bpy
from pathlib import Path
import os
import time
from datetime import date
from bpy.types import Operator

from . helpers import ShowMessageBox, make_render_context

class CROSBY_OT_playblast(Operator):
    bl_label = "Make playblast"
    bl_idname = "addonname.myop_playblast"
    bl_description = "Render a playblast to the dailies-folder."

    def execute(self, context):
        prev_renderpath = bpy.context.scene.render.filepath
        prev_renderengine = bpy.context.scene.render.engine
        prev_fileformat = bpy.context.scene.render.image_settings.file_format
        prev_fileext = bpy.context.scene.render.use_file_extension
        prev_gizmo = bpy.context.space_data.show_gizmo

        render_context = make_render_context()
        dailies_path = render_context["dailies_path"]
        if dailies_path is None:
            ShowMessageBox(message="No dailies folder found.")
            return {'CANCELLED'}

        projectname = os.path.split(bpy.data.filepath)[1]
        projectname = projectname.replace(".blend", "")

        d = date.strftime(date.today(),"%y%m%d")
        playblast_path = os.path.join(dailies_path, d, "playblasts", projectname + time.strftime("_%y%m%d_%H%M%S_", time.localtime()))

        bpy.context.scene.render.filepath = playblast_path
        bpy.context.scene.render.engine = "BLENDER_WORKBENCH"
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.ffmpeg.codec = "H264"
        bpy.context.scene.render.ffmpeg.format = "MPEG4"
        bpy.context.scene.render.use_file_extension = True
        bpy.context.space_data.show_gizmo = False

        bpy.ops.render.opengl(animation=True)

        bpy.context.scene.render.filepath = prev_renderpath
        bpy.context.scene.render.engine = prev_renderengine
        bpy.context.scene.render.image_settings.file_format = prev_fileformat
        bpy.context.scene.render.use_file_extension = prev_fileext
        bpy.context.space_data.show_gizmo = prev_gizmo

        message = "Rendered playblast to: " + playblast_path
        ShowMessageBox(message=message)

        return {'FINISHED'}
