from myrustlib import detect_lines, reduce_lines

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
    True,True,False,True,True
]
width = 5
height = 5
(horizontal, vertical) = split_by_orientation(detect_lines(test, width, height,1))

print(vertical)
print(reduce_lines(horizontal, vertical, 2))
