import bpy
import os
from bpy.types import Panel, Operator
   
        
# Script for setting renderpaths and flamenco settings/paths
class CROSBY_OT_setrenderstand(Operator):
    bl_label = "Set Render Standard"
    bl_idname = "addonname.myop_setrenderstand"
    bl_description = "Set renderpaths for all outputs."
    
    def execute(self, context):    
        
        #bpy.ops.flamenco.fetch_job_types(1,)
        #bpy.context.scene.flamenco_job_type = 'crosby-render'

        path = bpy.data.filepath #Full project path
        pathsplit = path.rsplit("\\", -1)
        projectname = pathsplit[1]
        
        filename = bpy.path.basename(bpy.context.blend_data.filepath)
        filterend = filename[-9:] # keeps the last 9 characters in the string
        version = filterend.replace(".blend", "") # removes .blend from the version number
        
        scenefilter = filename.replace(".blend", "") # removes .blend from the scenename
        scenename = scenefilter[:-5]
        
        renderpath = "G:\\" + projectname + "\\" + "01_assets" + "\\" + "renders" "\\" + "3d" + "\\" + scenename + "\\" + "v" + version + "\\" + scenename + "_v" + version + "_"
        nodepath = "G:\\" + projectname + "\\" + "01_assets" + "\\" + "renders" "\\" + "3d" + "\\" + scenename + "\\" + "v" + version + "\\Passes\\"
        
        checkversion = "G:\\" + projectname + "\\" + "01_assets" + "\\" + "renders" "\\" + "3d" + "\\" + scenename + "\\" + "v" + version

        checkpath = bpy.path.abspath(checkversion)
        rootrender = "G:\\" + projectname + "\\" + "01_assets" + "\\" + "renders" "\\" + "3d" + "\\" + scenename + "\\" + "v" + version + "\\"
        
        def ShowMessageBox(message = "", title = "Crosby Tools", icon = 'INFO'):

            def draw(self, context):
                self.layout.label(text=message)

            bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

     
        # Check whether the specified path exists or not
        isExist = os.path.exists(checkpath)
        if not isExist:

            #newpath = r'C:\Program Files\arbitrary' 
            os.makedirs(checkpath)
            

            
        #sets renderpath and filename
        bpy.context.scene.render.filepath = renderpath

        #sets paths for all composite node outputs
        scene = bpy.context.scene
        if bpy.context.scene.use_nodes is not False:
            for node in scene.node_tree.nodes:
                if node.type == 'OUTPUT_FILE':
                    
                    if node.label != "":
                        
                        node.base_path = nodepath + node.label + "_" + "v" + version + "_"
                        
                        ShowMessageBox("Paths set, COMP ON")
                        self.report({'INFO'}, "Paths set, COMP ON")
                        
                    else:
                        ShowMessageBox("Paths set, COMP ON / Unlabeled file outputs found!")
                        self.report({'WARNING'}, "Unlabeled file outputs found!")
                    
    
            return {'FINISHED'}
        else:
            ShowMessageBox("Renderpath is set / Comp is OFF")
            self.report({'INFO'}, "Renderpath is set / COMP IS OFF")
            
            return {'FINISHED'}

