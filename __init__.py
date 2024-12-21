# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from . import (bonegenerator, qc)

bl_info = {
    "name": "TF2 Game Animation Rigs",
    "author": "ByAnon",
    "version": (0, 3),
    "blender": (4, 4, 0),
    "category": "Porting"
}

def register():
    bonegenerator.register()
    qc.register()

def unregister():
    bonegenerator.unregister()
    qc.unregister
