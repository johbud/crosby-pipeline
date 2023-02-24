import bpy
import os
from bpy.types import Operator
from . helpers import ShowMessageBox, make_render_context

class CROSBY_OT_versionup(Operator):
    bl_label = "Version up"
    bl_idname = "addonname.myop_versionup"
    bl_description = "Increases the version number, then updates render paths and saves the file."

    def find_next_version(self, current_version):
        try_version = int(current_version[-3:]) + 1
        while try_version < 1000:
            new_version = "v" + '{:03d}'.format(try_version)
            if not os.path.exists(bpy.data.filepath.replace(current_version, new_version)):
                return new_version
            try_version = try_version + 1
        return None

    def execute(self, context):
        current_filename = os.path.split(bpy.data.filepath)[1].replace(".blend", "")
        if current_filename == "":
            ShowMessageBox("File has not been saved yet.")
            return {'CANCELLED'}
        current_version = current_filename[-4:]
        
        if current_version[0] != "v":
            ShowMessageBox("Could not determine version.")
            return {'CANCELLED'}
        
        if not str.isnumeric(current_version[-3:]):
            ShowMessageBox("Version is not a number!")
            return {'CANCELLED'}
        
        new_version = self.find_next_version(current_version)
        if not new_version:
            ShowMessageBox("Could not get next version.")
            return {'CANCELLED'}
                
        bpy.context.scene.render.filepath = bpy.context.scene.render.filepath.replace(current_version, new_version) 
        
        scene = bpy.context.scene
        if scene.use_nodes:
            for node in scene.node_tree.nodes:
                if node.type == 'OUTPUT_FILE':
                    node.base_path = node.base_path.replace(current_version, new_version)
                    if node.format.file_format == "PNG":
                        for slot in node.file_slots:
                            slot.path = slot.path.replace(current_version, new_version)

        new_filepath = bpy.data.filepath.replace(current_version, new_version)

        try:
            bpy.ops.wm.save_as_mainfile(filepath=new_filepath)
        except Exception as err:
            ShowMessageBox("Failed to save file: " + err)
            return {'CANCELLED'}
        
        render_context = make_render_context()

        if render_context is None:
            ShowMessageBox("Could not find render context.")
            return {'CANCELLED'}

        folder_path = os.path.split(render_context["render_path"])[0]
        
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        
        ShowMessageBox("File saved and paths updated. New version: " + new_version)

        return {'FINISHED'}