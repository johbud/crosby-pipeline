import bpy
import os
from bpy.types import Panel, Operator
from . helpers import make_render_context
   
        
# Script for setting renderpaths and flamenco settings/paths
class CROSBY_OT_setrenderstand(Operator):
    bl_label = "Set Render Standard"
    bl_idname = "addonname.myop_setrenderstand"
    bl_description = "Set renderpaths for all outputs."
    
    def execute(self, context):    
        
        #bpy.ops.flamenco.fetch_job_types(1,)
        #bpy.context.scene.flamenco_job_type = 'crosby-render'

        render_context = make_render_context()

        def ShowMessageBox(message = "", title = "Crosby Tools", icon = 'INFO'):

            def draw(self, context):
                self.layout.label(text=message)

            bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

     
        # Check whether the specified path exists or not
        if not os.path.exists(render_context['render_folder']):
            os.makedirs(render_context['render_folder'])
            
        #sets renderpath and filename
        bpy.context.scene.render.filepath = render_context['render_path']

        #sets paths for all composite node outputs
        scene = bpy.context.scene
        if bpy.context.scene.use_nodes is not False:
            for node in scene.node_tree.nodes:
                if node.type == 'OUTPUT_FILE':
                    
                    if node.label != "":
                        
                        node.base_path = os.path.join(render_context["render_path_passes"], node.label) 
                        
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

