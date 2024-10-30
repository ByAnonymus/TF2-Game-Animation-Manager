import bpy
from math import *

def angle(move_x, move_y):
    if sqrt(move_x*move_x+move_y*move_y) !=0:
        if move_x >=0 and move_y >=0:
            return max((degrees(asin(abs(move_y)/sqrt(move_x*move_x+move_y*move_y)))), (degrees(acos(abs(move_x)/sqrt(move_x*move_x+move_y*move_y)))))
        elif move_x <=0 and move_y >=0:
            return max((degrees(asin(abs(move_x)/sqrt(move_x*move_x+move_y*move_y)))), (degrees(acos(abs(move_y)/sqrt(move_x*move_x+move_y*move_y))))) + 90
        elif move_x <=0 and move_y <=0:
            return (max((degrees(asin(abs(move_y)/sqrt(move_x*move_x+move_y*move_y)))), (degrees(acos(abs(move_x)/sqrt(move_x*move_x+move_y*move_y))))) + 180)
        elif move_x >=0 and move_y <=0:
            return (max((degrees(asin(abs(move_x)/sqrt(move_x*move_x+move_y*move_y)))), (degrees(acos(abs(move_y)/sqrt(move_x*move_x+move_y*move_y))))) + 270)
        else:
            return 0
    else:
        return 0
def movement(angle, limit_right, limit_left, is_on_verge):
    if is_on_verge:
        if angle < limit_left:
            return (limit_left -angle)/45
        elif angle > limit_right:
            return (angle-limit_right)/45
        else:
            return 0
    else:
        if angle < limit_left and angle > limit_right:
            if limit_left - angle < angle-limit_right:
                return (limit_left -angle)/45
            elif limit_left - angle > angle-limit_right:
                return (angle-limit_right)/45
            else:
                return 1
        else:
            return 0



bpy.app.driver_namespace["angle"] = angle
bpy.app.driver_namespace["movement"] = movement