from square import *

squares = {
    'T':[
        [0,1,0],
        [1,1,1],
        [0,0,0]
        ],
    'I':[
        [0,0,0,0],
        [1,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
        ],
    'O':[
        [1,1],
        [1,1]
        ],
    'S':[
        [1,1,0],
        [0,1,1],
        [0,0,0],
        ],
    'Z':[
        [0,1,1],
        [1,1,0],
        [0,0,0],
        ],
    'L':[
        [0,0,1],
        [1,1,1],
        [0,0,0],
        ],
    'J':[
        [1,0,0],
        [1,1,1],
        [0,0,0],
        ],
    'X':[
        [0,1,0],
        [1,1,1],
        [0,1,0]
        ]
}

colors = {
    'T':(100,10,100),
    'I':(10,10,190),
    'O':(150,120,5),
    'S':(10,130,10),
    'Z':(140,3,5),
    'L':(200,90,10),
    'J':(20,20,130),
    'X':(34,124,53)
}

generic = {
    0:[(0, 0),( 0, 0),( 0, 0),( 0, 0),( 0, 0)],
    1:[(0, 0),(+1, 0),(+1, 1),( 0,-2),(+1,-2)],
    2:[(0, 0),( 0, 0),( 0, 0),( 0, 0),( 0, 0)],
    3:[(0, 0),(-1, 0),(-1, 1),( 0,-2),(-1,-2)]}
kick_table={
    'I':{
        0:[( 0, 0),( 0, 0),(-1, 0),(+2, 0),(-1, 0),(+2, 0)],
        1:[( 0, 0),(-1, 0),( 0, 0),( 0, 0),( 0,-1),( 0,+2)],
        2:[( 0, 0),(-1,-1),(+1,-1),(-2,-1),(+1, 0),(-2, 0)],
        3:[( 0, 0),( 0,-1),( 0,-1),( 0,-1),( 0,+1),( 0,-2)]
    },
    "T":generic,
    'S':generic,
    'Z':generic,
    'L':generic,
    'J':generic,
    'O':{
        0:[(0, 0)],
        1:[(0, 0)],
        2:[(0, 0)],
        3:[(0, 0)]
    },
    'X':{
        0:[(0, 0)],
        1:[(0, 0)],
        2:[(0, 0)],
        3:[(0, 0)]
    }
}

class Piece():
    def __init__(self,board,window,piece,size=32, max_staling_amount=10,max_staling_time=1,x=0,y=0,piece_syle=0):
        self.rotation = 0
        self.max_staling_amount = max_staling_amount
        self.max_staling_time = max_staling_time
        self.stalling_timer = 0
        self.stalled = 0

        self.x = x
        self.y = y
        self.z = 0
        self.piece = piece.upper()
        self.layout = squares[self.piece]
        self.squares = []
        self.size = size

        self.board = board
        self.window = window

        initial_x = x
        for row in self.layout:
            x = initial_x
            for col in row:
                if col == 1:
                    sq = Square(colors[self.piece],size=size,style=piece_syle)
                    sq.x = x
                    sq.y = y
                    self.squares.append(sq)
                x += size
            y += size
    
    def draw(self):
        for square in self.squares:
            square.draw()
        
    def draw_shadow_piece(self):
        x = self.x
        y = self.y

        height = 0
        valid = True
        while(valid):
            height += 1
            for piece in self.squares:
                if self.board.existent_square(piece.x,piece.y + self.size * height):
                    height -= 1
                    valid = False
                    break
                    
        self.y += height * self.size
        self.align()

        for square in self.squares:
            square.surface.set_alpha(100)
            square.draw()
            square.surface.set_alpha(255)

        self.x = x
        self.y = y
        self.align()
        
    
    def move_y(self,delta_amount):
        for piece in self.squares:
            if self.board.existent_square(piece.x,piece.y + self.size):
                self.stalling_timer += self.window.delta_time() * 0.5
                return

        self.z += delta_amount
        if self.z >= 1:
            for piece in self.squares:
                piece.y += self.size
            self.y += self.size
            self.z -= 1
    
    def move_x(self,delta_amount):
        for piece in self.squares:
            if self.board.existent_square(piece.x + (delta_amount * self.size),piece.y):
                return
        for piece in self.squares:
            piece.x += delta_amount * self.size
        self.x += delta_amount * self.size
        self.reset_stalling_timer()

    def hard_drop(self):
        y = 0
        valid = True
        while(valid):
            y += 1
            for piece in self.squares:
                if self.board.existent_square(piece.x,piece.y + self.size * y):
                    y -= 1
                    valid = False
                    self.stalled = self.max_staling_amount
                    break
                    
        self.y += y * self.size
        self.align()

    
    def rotate(self,rotation):
        width = len(self.layout[0])
        height = len(self.layout)
        initial_x = self.x
        rotated = []
        for x in range(width):
            initial_y = self.y
            row = []
            for y in range(height):
                if rotation == 1:
                    square = self.layout[height - 1 - y][x]
                elif rotation == -1:
                    square = self.layout[y][width - 1 - x]

                row.append(square)
                initial_y += self.size
            rotated.append(row)
            initial_x += self.size

        kick1, kick2 = kick_table[self.piece][self.rotation],kick_table[self.piece][self.add_rotate(rotation)]
        for kick_value in range(len(kick1)):
            new_kick_value = (kick1[kick_value][0] -  kick2[kick_value][0], kick1[kick_value][1] - kick2[kick_value][1])
            if self.validate_rotation(rotated,(new_kick_value)):
                self.layout = rotated
                self.x += new_kick_value[0] * self.size
                self.y += new_kick_value[1] * self.size
                self.align()
                self.rotation = self.add_rotate(rotation)
                self.reset_stalling_timer()
                return
    
    def reset_stalling_timer(self):
        if self.stalling_timer > 0:
            self.stalled += 1
        self.stalling_timer = 0
    
    def validate_rotation(self,new_pos,kick_value):
        for y in range(len(new_pos)):
            for x in range(len(new_pos[0])):
                if new_pos[y][x] == 1:
                    if self.board.existent_square((x + kick_value[0]) * self.size + self.x, (y + kick_value[1]) * self.size + self.y):
                        return False
        return True
        
    def add_rotate(self,delta):
        delta = delta % 4
        new_rotation = self.rotation

        if delta < 0:
            if new_rotation + delta < 0:
                new_rotation += 4 + delta
            else:
                new_rotation += delta
        elif delta > 0:
            if new_rotation + delta > 3:
                new_rotation += delta - 4
            else:
                new_rotation += delta

        return new_rotation

    def align(self):
        x = self.x
        y = self.y
        z = 0
        for row in self.layout:
            x = self.x
            for col in row:
                if col == 1:
                    self.squares[z].x = x
                    self.squares[z].y = y
                    z += 1
                x += self.size
            y += self.size


def l_print(l):
    for x in l:
        print(x)