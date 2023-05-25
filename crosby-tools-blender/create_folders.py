import bpy
import os
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from . helpers import ShowMessageBox, make_render_context
from . renderstandard import CROSBY_OT_setrenderstand

class CROSBY_OT_createfolder(Operator, ExportHelper):
    bl_label = "Create folders and save"
    bl_idname = "addonname.myop_createfolders"
    bl_description = "Creates work-, output- and dailies-folders, and saves the file."
    filename_ext = ""

    def execute(self, context):
        path, filename = os.path.split(self.filepath)
        work_folder = os.path.join(self.filepath, "01_work")
        output_folder = os.path.join(self.filepath, "02_output")
        dailies_folder = os.path.join(self.filepath, "03_dailies")
        os.makedirs(work_folder)
        os.makedirs(output_folder)
        os.makedirs(dailies_folder)

        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(work_folder, filename) + "_v001" + ".blend")

        bpy.ops.addonname.myop_setrenderstand()
        
        ShowMessageBox("Created folders and saved scene to:" + self.filepath)
        return {'FINISHED'}