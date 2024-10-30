import bpy
from . import (bonegenerator, qc)

bl_info = {
    "name": "TF2 Game Animation Rigs",
    "author": "ByAnon",
    "version": (0, 1),
    "blender": (4, 2, 0),
    "category": "Porting"
}

def register():
    bonegenerator.register()
    qc.register()

def unregister():
    bonegenerator.unregister()
    qc.unregister
