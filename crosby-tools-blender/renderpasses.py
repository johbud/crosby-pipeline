import bpy
import os
from bpy.types import Operator
from . helpers import make_render_context, ShowMessageBox

class CROSBY_OT_renderpasses(Operator):
    bl_label = "Set renderpasses"
    bl_idname = "addonname.myop_renderpasses"
    bl_description = "Set renderpasses and wire up compositor nodes for rendering."

    def make_nodes(self, tree, render_context, viewlayer=None):

        filename_split = render_context["filename"].split("_")
        version = filename_split.pop()
        filename = ""
        for part in filename_split:
            filename += part + "_"
        
        if viewlayer:
            filename += viewlayer.name

        node_output_rgb = tree.nodes.new(type="CompositorNodeOutputFile")
        node_output_rgb.format.file_format = "OPEN_EXR_MULTILAYER"
        node_output_rgb.format.color_mode = "RGBA"
        node_output_rgb.format.color_depth = "16"
        node_output_rgb.base_path = os.path.join(render_context["render_path_passes"], filename+"RGB_"+version+"_")
        if viewlayer:
            node_output_rgb.label = viewlayer.name + "_RGB"
        else:
            node_output_rgb.label = "RGB"

        node_output_data = tree.nodes.new(type="CompositorNodeOutputFile")
        node_output_data.format.file_format = "OPEN_EXR_MULTILAYER"
        node_output_data.format.color_mode = "RGBA"
        node_output_data.format.color_depth = "32"
        node_output_data.base_path = os.path.join(render_context["render_path_passes"], filename+"DATA_"+version+"_")
        if viewlayer:
            node_output_data.label = viewlayer.name + "_DATA"
        else:
            node_output_data.label = "DATA"

        node_output_crypto = tree.nodes.new(type="CompositorNodeOutputFile")
        node_output_crypto.format.file_format = "OPEN_EXR_MULTILAYER"
        node_output_crypto.format.color_mode = "RGBA"
        node_output_crypto.format.color_depth = "32"
        node_output_crypto.base_path = os.path.join(render_context["render_path_passes"], filename+"CRYPTO_"+version+"_")
        if viewlayer:
            node_output_crypto.label = viewlayer.name + "_CRYPTO"
        else:
            node_output_crypto.label = "CRYPTO"

        node_composite = tree.nodes.new(type="CompositorNodeComposite")

        node_renderlayer = tree.nodes.new(type="CompositorNodeRLayers")

        if viewlayer:
            node_renderlayer.layer = viewlayer.name

        links = tree.links
        links.new(node_renderlayer.outputs[0], node_composite.inputs[0])

        for output in node_renderlayer.outputs:
            if "Crypto" in output.name:
                input = node_output_crypto.file_slots.new(output.name)
                links.new(input, output)
            elif output.type == "RGBA":
                if output.name == "Image":
                    input = node_output_rgb.file_slots.new("rgba")
                else:
                    input = node_output_rgb.file_slots.new(output.name)
                links.new(input, output)
            else:
                input = node_output_data.file_slots.new(output.name)
                links.new(input, output)

        for slot in node_output_rgb.file_slots:
            if "Deprecated" in slot.name:
                node_output_rgb.file_slots.remove(slot)
        
        return

    def execute(self, context):

        render_context = make_render_context()

        if render_context is None:
            ShowMessageBox("Could not find render context. Cancelled.")
            return {'CANCELLED'}

        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        
        bpy.context.scene.render.engine = "CYCLES"

        for layer in bpy.context.scene.view_layers:
            
            # RGB passes            
            layer.use_pass_combined = True
            layer.use_pass_diffuse_direct = True
            layer.use_pass_diffuse_indirect = True
            layer.use_pass_diffuse_color = True
            layer.use_pass_glossy_direct = True
            layer.use_pass_glossy_indirect = True
            layer.use_pass_glossy_color = True
            layer.use_pass_transmission_direct = True
            layer.use_pass_transmission_indirect = True
            layer.use_pass_transmission_color = True
            layer.cycles.use_pass_volume_direct = True
            layer.cycles.use_pass_volume_indirect = True
            layer.use_pass_emit = True
            layer.use_pass_environment = True
            layer.use_pass_shadow = True
            layer.use_pass_ambient_occlusion = True

            # Data passes
            layer.use_pass_z = True
            layer.use_pass_position = True
            layer.use_pass_normal = True
            layer.use_pass_vector = True
            layer.use_pass_cryptomatte_object = True
            layer.pass_cryptomatte_depth = 2

        for node in tree.nodes:
            tree.nodes.remove(node)

        bpy.context.scene.render.filepath = render_context["render_path"]
        folder_path = os.path.split(render_context["render_path"])[0]
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        if len(bpy.context.scene.view_layers) < 2:
            try: 
                self.make_nodes(tree, render_context)
            except:
                ShowMessageBox("Failed to set outputs.")
        else: 
            for layer in bpy.context.scene.view_layers:
                try:
                    self.make_nodes(tree, render_context, layer)
                except:
                    ShowMessageBox("Failed to set outputs for layer: " + layer.name)
        
        ShowMessageBox("Successfully set renderpasses and outputs.")
        
        return {'FINISHED'}