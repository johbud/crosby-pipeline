import bpy
from bpy.types import Operator

# Script for check texture paths
class CROSBY_OT_validateimages(Operator):
    bl_label = "Check textures"
    bl_idname = "addonname.myop_validateimg"
    bl_description = "Check textures."
    
    def execute(self, context):
        
        def ShowMessageBox(message = "", title = "Crosby Tools", icon = 'INFO'):

            def draw(self, context):
                self.layout.label(text=message)

            bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
        
        conditions = ("G","g","R","r","//") #Valid paths
        
        texlist = [] #Create list for paths
                
        for x in bpy.data.images: #Loop through all images in scene
            #if not ((x.name== "Render Result") or (x.name== "Viewer Node") or (x.filepath.startswith(conditions)) and (x.packed_file == "PackedFile")):
            if not ((x.name== "Render Result") or (x.name== "Viewer Node") or (x.packed_file != None) or (x.filepath.startswith(conditions))):
                texlist.append(bpy.path.abspath(x.filepath)) #Add them to a list
         
              
        if not len(texlist) == 0:
            ShowMessageBox("Found " + str(len(texlist)) + " local files. Check info panel")
               
            self.report({'INFO'}, "--------------- Validation starts here ---------------") #Report number of local files
            
            for i in range(len(texlist)):
                self.report({'WARNING'}, str(texlist[i])) #Report all the paths
                
            bpy.ops.screen.info_log_show()    
            bpy.ops.info.select_all(action='SELECT')
            bpy.ops.info.report_delete()    
            self.report({'WARNING'}, "Found " + str(len(texlist)) + " local files.") #Report number of local files
            
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "Scene Passed")
            ShowMessageBox("Scene Passed")
            return {'FINISHED'}

