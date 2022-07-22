from square import *
from piece import *
from board import *
from PPlay.window import *
import pygame
import random

clock = pygame.time.Clock()
frame_rate = 60

settings = {
    'soft_drop_speed':1.5,
    'DAS':{
        'time':8/frame_rate,
        'speed':1/frame_rate
    }
}


controls = {
    'p1':{
        'left':'a',
        'right':'d',
        'rotate_r':'right',
        'rotate_l':'left',
        'hard_drop':'w',
        'soft_drop':'s',
        'hold':'q'
    },
    'p2':{
        'left':'f',
        'right':'h',
        'rotate_r':'l',
        'rotate_l':'k',
        'hard_drop':'t',
        'soft_drop':'g',
        'hold':'r'
    },     
}

time_held = {
    'left':0,
    'right':0,
    'right_das':0,
    'left_das':0,
    'rotate_l':0,
    'rotate_r':0,
    'hard_drop':0,
    'hold':0
}

pieze_size = 16
board_width = 10 + 2
queue_size = 4
hold_size = 6
board_height = 21

number_of_boards = 2

window = Window(pieze_size * (board_width + queue_size + hold_size) * number_of_boards,pieze_size * (board_height))
bg = pygame.Surface((window.width,window.height))
###################
boards = []

tetris_board = Board(window=window,width=10,height=20,size=16,x=6,y=0,piece_style=0,invisible_layers=0)

tetris_board.set_queue_size(4)
tetris_board.time_held = time_held.copy()
tetris_board.controls = controls['p1']
tetris_board.settings = settings

boards.append(tetris_board)


tetris_board = Board(window=window,width=10,height=20,size=16,x=12+16,y=0,piece_style=0)

tetris_board.set_queue_size(4)
tetris_board.damage_per_pass = 20
tetris_board.time_held = time_held.copy()
tetris_board.controls = controls['p2']
tetris_board.settings = settings

boards.append(tetris_board)

boards[0].opponents.append(boards[1])
boards[1].opponents.append(boards[0])
###################

keyboard = window.keyboard

# boards[0].take_damage(8)

while(True):

    window.get_screen().blit(bg,(0,0))

    for board in boards:
        board.movement()
        board.draw()

    for board in boards: 
        for attack in board.attack_balls:
            attack.main()

    clock.tick(frame_rate)
    window.update()