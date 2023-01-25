"""

Attributes:
    doc (c4d.documents.BaseDocument): The currently active document.
    op (c4d.BaseObject): The primary selected object in #doc. Cinema 4D can hold multiple objects
     selected, and then only the first object in that selection is reflected in #op. Can be #None. 
"""

import c4d
import redshift
import maxon
import typing
from pathlib import Path

doc: c4d.documents.BaseDocument
op: typing.Optional[c4d.BaseObject]

ID_BUTTON_SEND = 10000
ID_BUTTON_EXIT = 10001
ID_BUTTON_RSA = 10002
OK = 0
WARNING = 1
ERROR = 2


def main() -> None:
    dlg = ValidationDialog()
    dlg.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE, defaultw=700, defaulth=200)
    
    return

class ValidationDialog(c4d.gui.GeDialog):

    allowed_texture_drives = [
        "g:", "G:",
        "r:", "R:"
    ]

    format_names = {
        c4d.FILTER_TIF: "TIFF",
        c4d.FILTER_TGA: "TGA", 
        c4d.FILTER_BMP: "BMP",
        c4d.FILTER_IFF: "IFF",
        c4d.FILTER_JPG: "JPG",
        c4d.FILTER_PICT: "PICT",
        c4d.FILTER_PSD: "PSD",
        c4d.FILTER_RLA: "RLA",
        c4d.FILTER_RPF: "RPF",
        c4d.FILTER_B3D: "B3D (Bodypaint)",
        c4d.FILTER_TIF_B3D: "B3D Tiff (Bodypaint)",
        c4d.FILTER_PSB: "PSB",
        c4d.FILTER_AVI: "AVI video",
        c4d.FILTER_MOVIE: "Quicktime video",
        c4d.FILTER_HDR: "HDR",
        c4d.FILTER_PNG: "PNG",
        c4d.FILTER_IES: "IES",
        c4d.FILTER_EXR: "EXR",
        c4d.FILTER_EXR_LOAD: "EXR Load",
    }

    depth_names = {
        c4d.RDATA_FORMATDEPTH_8: "8 bit",
        c4d.RDATA_FORMATDEPTH_16: "16 bit",
        c4d.RDATA_FORMATDEPTH_32: "32 bit"
    }

    allowed_formats = [
        "PSD",
        "PSB",
        "JPG",
        "EXR",
        "TIFF",
        "PNG"
    ]

    def __init__(self):

        self.object_list = []

        self.checks = {
            "Camera": {},
            "Frame range": {},
            "Frame rate": {},
            "Frame step": {},
            "Resolution": {},
            "Render engine": {},
            "Filename": {},
            "Format": {},
            "Multipass filename": {},
            "Multipass format": {},
            "Takes": {},
            "Textures": {}
        }

        render_data = doc.GetActiveRenderData()
        frame_rate = render_data[c4d.RDATA_FRAMERATE]
        start_frame = render_data[c4d.RDATA_FRAMEFROM].GetFrame(int(frame_rate))
        end_frame = render_data[c4d.RDATA_FRAMETO].GetFrame(int(frame_rate))
        resolution = (int(render_data[c4d.RDATA_XRES]), int(render_data[c4d.RDATA_YRES]))

        self.checks["Camera"] = self.check_camera(doc.GetRenderBaseDraw().GetSceneCamera(doc).GetName())

        self.checks["Frame range"] = {
            "value": str(start_frame) + " - " + str(end_frame),
            "status": OK,
            "message": ""
        }

        self.checks["Frame rate"] = self.check_framerate(frame_rate)
        
        self.checks["Frame step"] = self.check_framestep(render_data[c4d.RDATA_FRAMESTEP])
        
        self.checks["Resolution"] = {
            "value": str(resolution[0]) + " x " + str(resolution[1]),
            "status": OK,
            "message": ""
        }

        self.checks["Render engine"] = self.check_renderengine(render_data[c4d.RDATA_RENDERENGINE])
        
        self.checks["Filename"] = self.check_filename(render_data[c4d.RDATA_PATH])
        
        self.checks["Format"] = self.check_format(render_data[c4d.RDATA_FORMAT], render_data[c4d.RDATA_FORMATDEPTH])
        
        self.checks["Multipass format"] = self.check_multipass_format(render_data[c4d.RDATA_MULTIPASS_SAVEIMAGE], render_data[c4d.RDATA_MULTIPASS_SAVEFORMAT], render_data[c4d.RDATA_MULTIPASS_SAVEDEPTH])
        self.checks["Multipass filename"] = self.check_multipass_filename(render_data[c4d.RDATA_MULTIPASS_SAVEIMAGE], render_data[c4d.RDATA_MULTIPASS_FILENAME])

        self.checks["Takes"] = self.check_takes()

        self.checks["Textures"] = self.check_textures()
        

        return


    def check_filename(self, _filename):
        filename = {
            "value": _filename,
            "status": OK,
            "message": ""
        }

        path = Path(filename["value"])

        if path.drive != "G:":
            filename["status"] = WARNING
            filename["message"] += "Render path not on server. "
        if not "01_assets" in path.parts:
            filename["status"] = WARNING
            filename["message"] += "Render path not in assets folder. "
        
        if filename["value"] == "":
            filename["status"] = ERROR
            filename["message"] = "No render path set! "

        return filename

    def check_format(self, _format, _depth):
        format = {
            "value": self.get_format(_format, _depth),
            "status": OK,
            "message": ""
        }

        if not self.format_names[_format] in self.allowed_formats:
            format["status"] = WARNING
            format["message"] = "Check format."

        return format


    def check_multipass_format(self, enabled, format, depth) -> dict:
        multipass_format = {
            "value": "",
            "status": OK,
            "message": ""
        }

        if self.format_names[format] != "EXR":
            multipass_format["status"] = WARNING
            multipass_format["message"] = "Check format, should be EXR."
        
        if enabled:
            multipass_format["value"] = self.get_format(format, depth)
        else:
            multipass_format["value"] = "Multipass disabled."

        return multipass_format


    def check_multipass_filename(self, enabled, filename) -> dict:
        multipass_filename = {
            "value": "",
            "status": OK,
            "message": ""
        }
        
        if enabled:
            multipass_filename["value"] = filename
            path = Path(filename)

            if path.drive != "G:":
                multipass_filename["status"] = WARNING
                multipass_filename["message"] += "Render path not on server. "
            if not "01_assets" in path.parts:
                multipass_filename["status"] = WARNING
                multipass_filename["message"] += "Render path not in assets folder. "
            if multipass_filename["value"] == "":
                multipass_filename["message"] = "No render path set!"
        else:
            multipass_filename["value"] = "Multipass disabled."

        return multipass_filename
        

    def check_camera(self, camera_name) -> dict:
        camera = {
            "value": "",
            "status": OK,
            "message": ""
        }

        camera_type_names = ["Camera", "RS Camera"]
        scene_camera = doc.GetRenderBaseDraw().GetSceneCamera(doc)

        obj = doc.GetFirstObject()
        self.GoDownHierarchy(obj)

        for obj in self.object_list:            
            if obj.GetTypeName() in camera_type_names:
                if scene_camera == obj:
                    camera["value"] = obj.GetName()
                    return camera

        camera["message"] = "No camera is active!"
        camera["status"] = WARNING
        
        return camera
    
    def GoDownHierarchy(self, obj):
        if obj is None: return
        self.object_list.append(obj)
        if (obj.GetDown()):
            self.GoDownHierarchy(obj.GetDown())
        if (obj.GetNext()):
            self.GoDownHierarchy(obj.GetNext())


    def check_framerate(self, _framerate) -> dict:
        framerate = {
            "value": int(_framerate),
            "status": OK,
            "message": ""
        }

        if framerate["value"] != 25:
            framerate["status"] = WARNING
            framerate["message"] = "Check if the framerate is correct."
        
        return framerate

    
    def check_framestep(self, _framestep) -> dict:
        framestep = {
            "value": int(_framestep),
            "status": OK,
            "message": ""
        }

        if framestep["value"] != 1:
            framestep["status"] = WARNING
            framestep["message"] = "Not every frame will render."
        
        return framestep

    def check_renderengine(self, engine_code) -> dict:
        renderengine = {
            "value": "",
            "status": OK,
            "message": ""
        }

        if engine_code == c4d.RDATA_RENDERENGINE_STANDARD:
            renderengine["value"] = "Standard"
        if engine_code == c4d.RDATA_RENDERENGINE_PREVIEWHARDWARE:
            renderengine["value"] = "Hardware Preview"
        if engine_code == c4d.RDATA_RENDERENGINE_PHYSICAL:
            renderengine["value"] = "Physical"
        if engine_code == 1036219:
            renderengine["value"] = "Redshift"
        else:
            renderengine["value"] = "Unknown"

        if renderengine["value"] != "Redshift":
            renderengine["status"] = WARNING
            renderengine["message"] = "Renderer is not Redshift."
        
        return renderengine


    def check_textures(self) -> dict:
        textures = {
            "value": "",
            "status": OK,
            "message": ""
        }

        tex_list = doc.GetAllTextures()
        for tex in tex_list:
            p = Path(tex[1])
            if not p.drive in self.allowed_texture_drives:
                textures["message"] = "Some textures not on supported network drives."
                textures["status"] = WARNING

        return textures


    def check_takes(self) -> dict:
        takes = {
            "value": "",
            "status": OK,
            "message": ""
        }

        take_data = doc.GetTakeData()
        main_take = take_data.GetMainTake()

        if main_take.GetDown():
            takes["value"] = "Document contains takes."
            current_take = take_data.GetCurrentTake()
            takes["message"] = "Current take: " + current_take.GetName()
            takes["status"] = WARNING

        else:
            takes["value"] = "No takes in document."
        
        return takes


    def get_format(self, format_id, depth_id) -> str:
        return self.format_names[format_id] + " " + self.depth_names[depth_id]


    def CreateLayout(self) -> bool:
        self.SetTitle("Validation")

        for key, value in self.checks.items():
            if self.GroupBegin(0, c4d.BFH_SCALEFIT, cols=3):
                self.GroupBorderSpace(5, 5, 5, 5)
                self.GroupBorder(c4d.BORDER_GROUP_TOP)
                self.AddStaticText(10, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 0, key)
                self.AddStaticText(10, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT | c4d.BFH_LEFT, 400, 0, value["value"])
                if value["status"] == OK:
                    self.AddStaticText(10, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT | c4d.BFH_LEFT, 0, 0, "OK")
                else:
                    self.AddStaticText(10, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT | c4d.BFH_LEFT, 0, 0, "WARNING: " + value["message"])
                
            self.GroupEnd()

        self.AddButton(ID_BUTTON_SEND, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, name="Open Deadline submitter")
        self.AddButton(ID_BUTTON_EXIT, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, name="Close")
            
        return True

    
    def Command(self, id: int, msg: c4d.BaseContainer) -> bool:
        
        if id == ID_BUTTON_SEND:
            self.Close()
            c4d.CallCommand(1025665)

        if id == ID_BUTTON_EXIT:
            self.Close()

        return True

if __name__ == '__main__':
    main()
