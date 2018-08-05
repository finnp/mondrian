def reduce_lines(lines):
    """
        Takes a list of vertical and horizontal lines,
        tries to reduce them to essential lines eliminating lines close to each
        other.
    """
    already_seen = set()
    horizontal_lines = []
    vertical_lines = []
    min_distance = 50 # minimal distance for lines to be considered distinct
    for index, line in enumerate(lines):
        x1,y1,x2,y2 = line[0]
        if index in already_seen:
            continue
        if (abs(y1-y2) > abs(x1-x2)):
            # vertical
            for other_index, other_line in enumerate(lines):
                x1_other,y1_other,x2_other,y2_other = other_line[0]
                if (abs(x1 - x1_other) < min_distance):
                    if (y2_other < y2):
                        y2 = y2_other
                    if (y1_other > y1):
                        y1 = y1_other

                    already_seen.add(other_index)
            vertical_lines.append((x1,y1,x2,y2))
        else:
            #horizontal
            for other_index, other_line in enumerate(lines):
                x1_other,y1_other,x2_other,y2_other = other_line[0]
                if (abs(y1 - y1_other) < min_distance):
                    already_seen.add(other_index)

            horizontal_lines.append((x1,y1,x2,y2))
    return (vertical_lines, horizontal_lines)



def connect_lines(horizontal_lines, vertical_lines):
    """
        Makes sure the ends of every line are touching another line

        Possible improvements:
            - Prefer crossing lines in the direction of the end
                - e.g. the right end of a horizontal should rather connect to a vertical to the closest_vertical_right
            - Make sure the "crossing line" is actually long enough to cross this line

        Idea:
            - Test and improve this algorithm by
                - 1. create lines a la mondrian
                - 2. randomly shorten this lines
                - 3. run the algorithm over the sortened version
                - 4. check whether the result is the original
    """
    lines = []

    for x1,y1,x2,y2 in horizontal_lines:
        closest_vertical_left = 20000
        closest_vertical_right = 20000
        for v_x1,v_y1,v_x2,v_y2 in vertical_lines:
            if abs(x1 - v_x1) < abs(closest_vertical_left):
                closest_vertical_left = x1 - v_x1
            if abs(x2 - v_x1) < abs(closest_vertical_right):
                closest_vertical_right = x2 - v_x1
        x1 = x1 - closest_vertical_left
        x2 = x2 - closest_vertical_right
        lines.append((x1,y1,x2,y2))

    for x1,y1,x2,y2 in vertical_lines:
        closest_horizontal_up = 20000
        closest_horizontal_down = 20000
        for h_x1,h_y1,h_x2,h_y2 in horizontal_lines:
            if abs(y1 - h_y1) < abs(closest_horizontal_up):
                closest_horizontal_up = y1 - h_y1
            if abs(y2 - h_y1) < abs(closest_horizontal_down):
                closest_horizontal_down = y2 - h_y1
        y1 = y1 - closest_horizontal_up
        y2 = y2 - closest_horizontal_down
        lines.append((x1,y1,x2,y2))

    return lines
