import time
import random
import LCD1602 as LCD
from gpiozero import Button

GRASS_FRAMES = [
    [0b00000, 0b00000, 0b00000, 0b00000, 0b00001, 0b00001, 0b00011, 0b00011],
    [0b00000, 0b00000, 0b00000, 0b00010, 0b00111, 0b00111, 0b01111, 0b01111],
    [0b00000, 0b00000, 0b00000, 0b10000, 0b11000, 0b11000, 0b11100, 0b11100],
    [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b10000, 0b10000],
]

MAN_FRAMES = [
    [0b00000, 0b00000, 0b00000, 0b01110, 0b11111, 0b10101, 0b11111, 0b01110],
    [0b00000, 0b00000, 0b00000, 0b00100, 0b01110, 0b11111, 0b10101, 0b11111],
    [0b11111, 0b01110, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    [0b00000, 0b01110, 0b10101, 0b11111, 0b01110, 0b00000, 0b00000, 0b00000],
]


COL = 16  # LCD size: 2 row, 16 col
JUMP_CYCLE = 16
GOAL_SCORE = 11  # When score == GOAL_SCORE, you win.
MAX_SCORE_LEN = 3  # Maximum score length is 3. In other words, maximum score is 999.

# 0 : there is no grass here
# 1 : grass frame 1 here
# 2 : grass frame 2 here
# 3 : grass frame 3 here
# 4 : grass frame 4 here
grass_status = [0] * COL
grass_old_status = [0] * COL

# 0 : initial position(stand still)
# 1 ~ JUMP_CYCLE-1 : jumping
jump_status = 0
jump_old_status = 0

jump_order = False
game_start = False

score = 0
score_old = 0


button = Button(17)


def btn_pressed():
    global game_start
    global jump_order
    if game_start == False:
        game_start = True
    else:
        jump_order = True


button.when_pressed = btn_pressed


def game_status_init():
    global grass_status
    global grass_old_status
    global jump_status
    global jump_old_status
    global jump_order
    global game_start
    global score
    global score_old

    grass_status = [0] * COL
    grass_old_status = [0] * COL
    jump_status = 0
    jump_old_status = 0
    jump_order = False
    game_start = False
    score = 0
    score_old = 0


def get_grass_age():
    i = COL - 1
    while i >= 0:
        if grass_status[i] != 0:
            return COL - i
        i = i - 1
    return COL + 1


def update_grass_status():
    global score
    i = 0
    while i < COL:
        # For each grass_status[i], its loop is 0 -> 1 -> 2 -> 3 -> 4 -> 0
        # How does the grass move?
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2]
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3]
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 4]
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 0]
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 4, 0]
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 0, 0]
        #
        # ...
        #
        # [0, 0, 0, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # [0, 0, 0, 2, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        # [0, 0, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2]
        # [0, 0, 2, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3]
        # [0, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 4]
        # [0, 2, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 0]
        # [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 4, 0]
        # [2, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 0, 0]
        # [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 4, 0, 0]
        # [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0]
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 4, 0, 0, 0]

        if grass_status[i] == 0:
            i = i + 1
        elif grass_status[i] == 1:
            if i == COL - 1:
                grass_status[i] = 2
                return
            else:
                grass_status[i] = 2
                grass_status[i + 1] = 4
                i = i + 2
        elif grass_status[i] == 2:
            grass_status[i] = 3
            if i != 0:
                grass_status[i - 1] = 1
            if i != COL - 1:
                grass_status[i + 1] = 0
            i = i + 1
        elif grass_status[i] == 3:
            grass_status[i] = 4
            i = i + 1
        else:
            # grass_status[i] == 4
            grass_status[i] = 0
            if i == 0:
                score = score + 1  # because GRASS pass successfully, score = score + 1
            i = i + 1


def display_grass_status(index):
    LCD.send_command(0x80 + 0x40 * 1 + index)
    if grass_status[index] == 0:
        LCD.send_data(ord(" "))
    else:
        LCD.send_data(grass_status[i] - 1)


def display_jump_status():
    if jump_status == 0:
        if jump_old_status == JUMP_CYCLE - 1:
            LCD.print_num(0, 0, ord(" "))
            LCD.print_num(0, 1, 4)
    elif jump_status == 2:
        LCD.print_num(0, 0, 5)
        LCD.print_num(0, 1, 6)
    elif jump_status == 4:
        LCD.print_num(0, 0, 4)
        LCD.print_num(0, 1, ord(" "))
    elif jump_status == 8:
        LCD.print_num(0, 0, 7)
    elif jump_status == 12:
        LCD.print_num(0, 0, 4)
    elif jump_status == 14:
        LCD.print_num(0, 0, 5)
        LCD.print_num(0, 1, 6)


def update_jump_status():
    global jump_status
    global jump_order
    # for jump_status, its loop is 0 -> 1 -> 2 -> ... -> JUMP_CYCLE-1 -> 0
    if jump_status == 0:
        if jump_order:
            jump_status = 1  # handle jump order
    else:
        jump_status = (jump_status + 1) % JUMP_CYCLE

    # jump order should be cleared after it has been handled
    # if jump order comes when still jumping, it should be ignored
    jump_order = False


def write_user_characters():
    """
    write special characters into LCD's CGRAM
    """
    LCD.send_command(0x40)
    for frame in GRASS_FRAMES:
        for line in frame:
            LCD.send_data(line)
    for frame in MAN_FRAMES:
        for line in frame:
            LCD.send_data(line)


if __name__ == "__main__":
    while True:
        game_status_init()
        LCD.init_lcd()
        # LCD.turn_light(0) # turn the light off
        write_user_characters()
        LCD.print_str(5, 0, "JUMP!")
        LCD.print_str(1, 1, "Press To START")

        game_start = False
        # wait until button pressed
        while game_start == False:
            time.sleep(0.2)

        LCD.print_str(0, 1, " " * 16)
        LCD.print_str(15, 0, "0")
        LCD.print_num(0, 1, 4)
        jump_order = False
        while True:
            # new grass coming!
            # get_grass_age() > 8 ensure distance between grass greater than 8
            # random.random() > 0.9 cause uncertainty and make the game more interesting
            if get_grass_age() > 8 and random.random() > 0.9:
                grass_status[-1] = 1

            # compare new grass status with old grass status
            i = 0
            while i < COL:
                if grass_old_status[i] != grass_status[i]:
                    display_grass_status(i)  # show the difference
                    grass_old_status[i] = grass_status[i]
                i = i + 1

            # compare new jump status with old jump status
            if jump_status != jump_old_status:
                display_jump_status()  # show the difference
                jump_old_status = jump_status

            # if collide, game over
            if jump_status == 0 and grass_status[0] != 0:
                break

            update_grass_status()
            update_jump_status()

            # compare new score with old score
            if score != score_old:
                score_str = str(score)
                score_str = ((MAX_SCORE_LEN - len(score_str)) * " ") + score_str
                LCD.print_str(13, 0, score_str)  # show the difference
            if score == GOAL_SCORE:
                break

        LCD.print_str(0, 0, " " * 13)
        LCD.print_str(0, 1, " " * 16)
        LCD.print_str(10 - len(str(score)), 0, "score:")

        if score == GOAL_SCORE:
            LCD.print_str(4, 1, "YOU WIN!")
        else:
            LCD.print_str(3, 1, "GAME OVER!")
        game_start = False

        # wait until button pressed
        while game_start == False:
            time.sleep(0.2)
