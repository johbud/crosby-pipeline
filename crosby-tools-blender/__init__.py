bl_info = {
    "name": "Crosby Menu",
    "author": "Roberth S, John B",
    "version": (1, 5),
    "blender": (3, 4, 0),
    "location": "View3D > Main panel > Crosby",
    "description": "Collection of custom tools",
    "warning": "",
    "doc_url": "",
    "category": "Custom Tools",
}

import bpy
from bpy.types import Panel

from . playblast import CROSBY_OT_playblast
from . renderpasses import CROSBY_OT_renderpasses
from . pack_images import CROSBY_OT_packimages
from . purge_data import CROSBY_OT_purgedata
from . validate_cache import CROSBY_OT_validatecache
from . validate_images import CROSBY_OT_validateimages
from . validate_volumes import CROSBY_OT_validatevolumes
from . version_up import CROSBY_OT_versionup
from . current_renderpasses import CROSBY_OT_current_renderpasses
from . renderstandard import CROSBY_OT_setrenderstand
from . lightgroups import CROSBY_OT_lightgroups
 
class ADDONNAME_PT_main_panel(Panel):
    bl_label = "Crosby Tools"
    bl_idname = "ADDONNAME_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CROSBY"
 
    def draw(self, context):
        layout = self.layout
        
        layout.operator("addonname.myop_validateimg")
        layout.operator("addonname.myop_validatevols")
        layout.operator("addonname.myop_validatecache")
        layout.operator("addonname.myop_packimgs")
        layout.operator("addonname.myop_purgedata")
        layout.operator("addonname.myop_playblast")
        layout.operator("addonname.myop_renderpasses")
        layout.operator("addonname.myop_current_renderpasses")
        layout.operator("addonname.myop_versionup")
        layout.operator("addonname.myop_setrenderstand")
        layout.operator("addonname.myop_lightgroups")

classes = [ADDONNAME_PT_main_panel, CROSBY_OT_validateimages, CROSBY_OT_packimages, CROSBY_OT_validatevolumes, CROSBY_OT_validatecache, CROSBY_OT_purgedata, CROSBY_OT_playblast, CROSBY_OT_renderpasses, CROSBY_OT_versionup, CROSBY_OT_current_renderpasses, CROSBY_OT_setrenderstand, CROSBY_OT_lightgroups]
 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
 
 
if __name__ == "__main__":
    register()