import bpy
from bpy.types import Operator
from .helpers import ShowMessageBox


class CROSBY_OT_denoise_aovs(Operator):
    """Add denoise nodes for color AOV:s."""

    bl_label = "Denoise AOV:s"
    bl_idname = "addonname.myop_denoise_aovs"
    bl_description = "Add denoise nodes for color AOV:s."

    def execute(self, context):
        # Check that there are compositor nodes in the scene.
        if not bpy.context.scene.use_nodes:
            ShowMessageBox("Scene is not using the compositor. Cancelled.")
            return {"CANCELLED"}

        # Check that scene is using Cycles
        if not bpy.context.scene.render.engine == "CYCLES":
            ShowMessageBox("Scene is not using Cycles. Cancelled.")
            return {"CANCELLED"}

        # Add the denoise AOV:s
        for layer in bpy.context.scene.view_layers:
            layer.cycles.denoising_store_passes = True

        tree = bpy.context.scene.node_tree

        for node in tree.nodes:
            if not node.type == "OUTPUT_FILE":
                print("not OUTPUT_FILE, skipping")
                continue

            for node_input in node.inputs:
                print(node_input.name)
                if not node_input.type == "RGBA":
                    print("not RGBA, skipping")
                    continue
                if (
                    "Crypto" in node_input.name
                    or "crypto" in node_input.name
                    or "Deprecated" in node_input.name
                ):
                    print("crypto or depr, skipping")
                    continue
                if not node_input.is_linked:
                    print("not linked, skipping")
                    continue

                source = node_input.links[0].from_socket
                print(source.node.type)
                if not source.node.type == "R_LAYERS":
                    continue

                denoise_node = tree.nodes.new(type="CompositorNodeDenoise")
                denoise_albedo_input: bpy.types.NodeSocket
                denoise_normal_input: bpy.types.NodeSocket
                denoise_image_input: bpy.types.NodeSocket

                for denoise_input in denoise_node.inputs:
                    if denoise_input.name == "Albedo":
                        denoise_albedo_input = denoise_input
                    if denoise_input.name == "Normal":
                        denoise_normal_input = denoise_input
                    if denoise_input.name == "Image":
                        denoise_image_input = denoise_input

                for node_output in source.node.outputs:
                    if node_output.name == "Denoising Normal":
                        tree.links.new(denoise_normal_input, node_output)
                    if node_output.name == "Denoising Albedo":
                        tree.links.new(denoise_albedo_input, node_output)
                tree.links.new(denoise_image_input, source)
                tree.links.new(node_input, denoise_node.outputs[0])

        ShowMessageBox("Successfully added denoise nodes.")
        return {"FINISHED"}
