import bpy
from bpy.types import Operator

# Script for check Volume paths
class CROSBY_OT_purgedata(Operator):
    bl_label = "Remove unused data"
    bl_idname = "addonname.myop_purgedata"
    bl_description = "Remove unused data"
    
    def execute(self, context):
        
        def ShowMessageBox(message = "", title = "Crosby Tools", icon = 'INFO'):

            def draw(self, context):
                self.layout.label(text=message)

            bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    
        bpy.ops.outliner.orphans_purge(do_recursive=True)
        
        self.report({'INFO'}, "Unused data removed")
        ShowMessageBox("Unused data removed")
        return {'FINISHED'}
