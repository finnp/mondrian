from myrustlib import detect_lines
test = [
    True, True, True,True,True,
    False,False,False,True,False,
    False,False,False,False,False,
    True,True,False,True,True
]
width = 5
height = 4
print(detect_lines(test, width, height,2))
