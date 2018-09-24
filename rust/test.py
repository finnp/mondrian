from myrustlib import detect_lines, reduce_lines, write_line_length
import lines
import numpy as np

def split_by_orientation(lines):
    horizontal = []
    vertical = []
    for x1,y1,x2,y2 in lines:
        if (abs(y1-y2) > abs(x1-x2)):
            vertical.append((x1,y1,x2,y2))
        else:
            horizontal.append((x1,y1,x2,y2))
    return (horizontal, vertical)

test = [
    True, True, True,True,True,
    True, True, True,True,True,
    True,True,False,True,False,
    True,True,False,False,False,
    True,True,False,True,True,
    True,True,False,True,True
]
width = 5
height = 6
(horizontal, vertical) = split_by_orientation(detect_lines(test, width, height,1))

horizontal = [(8, 334, 148, 334), (0, 335, 521, 335), (0, 336, 625, 336), (701, 336, 787, 336), (801, 336, 853, 336), (0, 337, 863, 337), (0, 338, 863, 338), (0, 339, 863, 339), (0, 340, 863, 340), (0, 341, 863, 341), (0, 342, 863, 342), (0, 343, 863, 343), (8, 344, 863, 344), (10, 345, 863, 345), (21, 346, 165, 346), (203, 346, 863, 346), (271, 347, 340, 347), (355, 347, 863, 347), (448, 348, 550, 348), (593, 348, 768, 348), (318, 418, 366, 418), (0, 419, 678, 419), (0, 420, 863, 420), (0, 421, 863, 421), (0, 422, 863, 422), (0, 423, 863, 423), (0, 424, 863, 424), (0, 425, 863, 425), (0, 426, 863, 426), (0, 427, 863, 427), (0, 428, 863, 428), (6, 429, 863, 429), (28, 430, 863, 430), (725, 431, 863, 431), (21, 476, 305, 476), (6, 477, 658, 477), (0, 478, 863, 478), (0, 479, 863, 479), (0, 480, 863, 480), (0, 481, 863, 481), (0, 482, 863, 482), (0, 483, 863, 483), (7, 484, 863, 484), (128, 485, 863, 485), (163, 486, 359, 486), (402, 486, 863, 486), (246, 487, 344, 487), (455, 487, 543, 487), (611, 487, 815, 487), (619, 488, 669, 488), (0, 583, 663, 583), (679, 583, 755, 583), (0, 584, 863, 584), (0, 585, 863, 585), (0, 586, 863, 586), (0, 587, 863, 587), (0, 588, 863, 588), (0, 589, 863, 589), (0, 590, 863, 590), (0, 591, 863, 591), (0, 592, 863, 592), (33, 593, 122, 593), (134, 593, 863, 593), (161, 594, 863, 594), (225, 595, 502, 595), (516, 595, 561, 595), (576, 595, 668, 595), (684, 595, 863, 595), (240, 596, 310, 596), (416, 596, 486, 596), (690, 596, 863, 596), (694, 597, 780, 597), (813, 597, 857, 597), (537, 801, 621, 801), (467, 802, 700, 802), (467, 803, 700, 803), (467, 804, 700, 804), (467, 805, 700, 805), (467, 806, 700, 806), (467, 807, 700, 807), (467, 808, 700, 808), (467, 809, 700, 809), (639, 810, 700, 810), (467, 866, 701, 866), (467, 867, 701, 867), (467, 868, 701, 868), (467, 869, 701, 869), (467, 870, 701, 870), (467, 871, 701, 871), (467, 872, 701, 872), (467, 873, 701, 873), (467, 874, 701, 874), (467, 875, 701, 875), (467, 876, 611, 876), (625, 876, 701, 876)]
height = 956
width = 864

# print(vertical)
# print(horizontal)
h,v = write_line_length(height,width,horizontal,vertical)
print(len(h))
print(len([a for a in h if a]))
# print(filter(v))

# print(lines.reduce_lines(horizontal, vertical, 2))
# print(reduce_lines(horizontal, vertical, 2))
