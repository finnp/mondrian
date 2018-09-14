from lines import separate_ranges

# @todo: Just a todo test

# TODO: Another todo test

print(separate_ranges([
    (1,9),
    (1,2),
    (5,6),
    (8,9)
]))

print(separate_ranges([
    (1,2),
    (5,6),
    (8,9),
    (1,9)
]))

print(separate_ranges([
    (1,6),
    (7,8),
]))

print(separate_ranges([
    (1,6),
    (7,10),
    (8,9),
    (2,3)
]))
