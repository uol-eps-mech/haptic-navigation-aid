from random import randint


def get_heading():
    heading = randint(0, 360)
    return heading


required_movement_direction = (0, 1)


heading = get_heading()

current_heading = heading
current_heading1 = 8*heading
current_heading2 = 8*heading/360
current_heading3 = round(8*heading/360, 0)
current_heading4 = 8*heading//360
print(current_heading)
print(current_heading1)
print(current_heading2)
print(current_heading3)
print(current_heading4)
