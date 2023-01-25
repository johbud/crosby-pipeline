import bpy
from bpy.types import Operator

# Script for check Volume paths
class CROSBY_OT_validatevolumes(Operator):
    bl_label = "Check volumes"
    bl_idname = "addonname.myop_validatevols"
    bl_description = "Check volumes."
    
    def execute(self, context):
        
        def ShowMessageBox(message = "", title = "Crosby Tools", icon = 'INFO'):

            def draw(self, context):
                self.layout.label(text=message)

            bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
        
        conditions = ("G","g","R","r","//") #Valid paths
        
        vollist = [] #Create list for paths
                
        for x in bpy.data.volumes: #Loop through all images in scene
           
            if not x.filepath.startswith(conditions):
                vollist.append(bpy.path.abspath(x.filepath)) #Add them to a list
         
              
        if not len(vollist) == 0:
            ShowMessageBox("Found " + str(len(vollist)) + " local files. Check info panel")
               
            self.report({'INFO'}, "--------------- Validation starts here ---------------") #Report number of local files
            
            for i in range(len(vollist)):
                self.report({'WARNING'}, str(vollist[i])) #Report all the paths
                
            bpy.ops.screen.info_log_show()    
            bpy.ops.info.select_all(action='SELECT')
            bpy.ops.info.report_delete()    
            self.report({'WARNING'}, "Found " + str(len(vollist)) + " local files.") #Report number of local files
            
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "Scene Passed")
            ShowMessageBox("Scene Passed")
            return {'FINISHED'}

