import bpy
from bpy.types import Operator


# Script for packing local textures not located in G:\ or R:\
class CROSBY_OT_packimages(Operator):
    bl_label = "Pack local textures"
    bl_idname = "addonname.myop_packimgs"
    bl_description = "Pack local textures."

    def execute(self, context):
        def ShowMessageBox(message="", title="Crosby Tools", icon="INFO"):
            def draw(self, context):
                self.layout.label(text=message)

            bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

        conditions = ("G", "g", "R", "r", "//")  # Valid paths

        texlist = []  # Create list for paths

        for x in bpy.data.images:  # Loop through all images in scene
            if not (
                (x.name == "Render Result")
                or (x.name == "Viewer Node")
                or (x.packed_file != None)
                or (x.filepath.startswith(conditions))
            ):
                texlist.append(bpy.path.abspath(x.filepath))  # Add them to a list
                x.pack()

        if not len(texlist) == 0:
            ShowMessageBox(
                "Packed " + str(len(texlist)) + " local files. Save scene to apply"
            )

            self.report(
                {"INFO"}, "--------------- Packed following textures ---------------"
            )  # Report number of local files

            for i in range(len(texlist)):
                self.report({"INFO"}, str(texlist[i]))  # Report all the paths

            # bpy.ops.screen.info_log_show()
            # bpy.ops.info.select_all(action='SELECT')
            # bpy.ops.info.report_delete()
            self.report(
                {"WARNING"}, "Found " + str(len(texlist)) + " local files."
            )  # Report number of local files

            return {"FINISHED"}
        else:
            self.report({"INFO"}, "Scene Passed")
            ShowMessageBox("Scene Passed")
            return {"FINISHED"}
