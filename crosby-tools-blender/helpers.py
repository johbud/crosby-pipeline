import bpy
from pathlib import Path
import os


def make_render_context():
    render_context = {}
    render_context["filepath"] = bpy.data.filepath
    render_context["filename"] = os.path.split(render_context["filepath"])[1].replace(".blend", "")

    assets_path = None
    for parent in Path(bpy.data.filepath).parents:
        try_path = Path(os.path.join(parent,"01_assets"))        
        if try_path.exists():
            assets_path = try_path
            break
    
    if assets_path is None:
        return None
    
    dailies_path = None
    for parent in Path(bpy.data.filepath).parents:
            try_path = Path(os.path.join(parent,"03_dailies"))
            if try_path.exists():
                dailies_path = try_path
                break
            dailies_path = None

    if dailies_path is None:
        return None

    render_context["scenename"] = render_context["filename"][:-5]
    render_context["version"] = render_context["filename"][-4:]
    render_context["render_path"] = os.path.join(assets_path, "renders", "3d", render_context["scenename"], render_context["version"], render_context["filename"] + "_")
    render_context["render_path_passes"] = os.path.join(assets_path, "renders", "3d", render_context["scenename"], render_context["version"], "passes")
    render_context["dailies_path"] = dailies_path

    if not os.path.exists(os.path.join(assets_path, "renders", "3d", render_context["scenename"])):
        os.mkdir(os.path.join(assets_path, "renders", "3d", render_context["scenename"]))
    if not os.path.exists((os.path.join(assets_path, "renders", "3d", render_context["scenename"], render_context["version"]))):
        os.mkdir(os.path.join(assets_path, "renders", "3d", render_context["scenename"], render_context["version"]))

    return render_context


def ShowMessageBox(message = "", title = "Crosby Tools", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
