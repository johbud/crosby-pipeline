import bpy
import os
from bpy.types import Operator
from . helpers import make_render_context, ShowMessageBox

class CROSBY_OT_current_renderpasses(Operator):
    bl_label = "Set outputs for renderpasses"
    bl_idname = "addonname.myop_current_renderpasses"
    bl_description = "Wire up compositor nodes for rendering current passes."

    def make_nodes(self, tree, render_context, viewlayer=None):

        currentlayername = bpy.context.view_layer.name
        filename = render_context["filename"]
        if viewlayer:
            filename = filename + "_" + viewlayer.name

        node_output_rgb = tree.nodes.new(type="CompositorNodeOutputFile")
        node_output_rgb.format.file_format = "OPEN_EXR_MULTILAYER"
        node_output_rgb.format.color_mode = "RGBA"
        node_output_rgb.format.color_depth = "16"
        node_output_rgb.base_path = os.path.join(render_context["render_path_passes"], render_context["filename"]+"_RGB_")
        node_output_rgb.label = currentlayername
        
        #node_output_data = tree.nodes.new(type="CompositorNodeOutputFile")
        #node_output_data.format.file_format = "OPEN_EXR_MULTILAYER"
        #node_output_data.format.color_mode = "RGBA"
        #node_output_data.format.color_depth = "32"
        #node_output_data.base_path = os.path.join(render_context["render_path_passes"], render_context["filename"]+"_DATA_")

        node_output_crypto = tree.nodes.new(type="CompositorNodeOutputFile")
        node_output_crypto.format.file_format = "OPEN_EXR_MULTILAYER"
        node_output_crypto.format.color_mode = "RGBA"
        node_output_crypto.format.color_depth = "32"
        node_output_crypto.base_path = os.path.join(render_context["render_path_passes"], render_context["filename"]+"_CRYPTO_")
        node_output_crypto.label = currentlayername + "_Crypto"

        node_composite = tree.nodes.new(type="CompositorNodeComposite")

        node_renderlayer = tree.nodes.new(type="CompositorNodeRLayers")

        if viewlayer:
            node_renderlayer.layer = viewlayer.name

        links = tree.links
        links.new(node_renderlayer.outputs[0], node_composite.inputs[0])

        for output in node_renderlayer.outputs:
            if output.enabled == True:
                if "Crypto" in output.name:
                    input = node_output_crypto.file_slots.new(output.name)
                    links.new(input, output)
                else:
                    if output.name == "Image":
                        input = node_output_rgb.file_slots.new("rgba")
                    else:
                        input = node_output_rgb.file_slots.new(output.name)
                    links.new(input, output)
               
        
        return


    def execute(self, context):

        currentlayer = bpy.context.view_layer
        render_context = make_render_context()

        if render_context is None:
            ShowMessageBox("Could not find render context. Cancelled.")
            return {'CANCELLED'}

        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        
        bpy.context.scene.render.engine = "CYCLES"


        self.make_nodes(tree, render_context, currentlayer)

        
        
        ShowMessageBox("Successfully set renderpasses and outputs.")
        
        return {'FINISHED'}