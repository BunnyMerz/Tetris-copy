from square import *
from piece import *
import random
from attack_ball import AttackBall

solid_color = (70,70,70)
damage_color = (90,90,90)

class Board():
    def __init__(self,window,width,height,size=32,invisible_layers=0,queue_size=5,x=0,y=0,piece_style=0):
        self.window = window

        self.damage_queue = 0
        self.damage_per_pass = 8
        self.clear_avoids_damage = True ## Damage per pass = 0 has the same effect as this line = True
        self.hold_damage = False ## Never used. Maybe a diff version of clear_avoids_damage by mistake.
        self.opponents = []
        
        self.x = x * size
        self.y = y * size
        self.gravity = 0.1

        self.btb = 0
        self.combo = 0

        self.piece = None
        self.held = False
        self.hold_piece = None
        self.show_shadow_piece = True
        self.hide_board = False

        self.width = width
        self.height = height
        self.size = size
        self.piece_style = piece_style
        self.invisible_layers = invisible_layers
        self.board_grid = []
        self.attack_balls = []

        self.controls = {}
        self.time_held = {}
        self.settings = {}

        self.spawn_point = [self.size * 4 + self.x,0 + self.y]

        self.piece_bag_default = ['S','Z','T','O','I','L','J']
        self.bag = self.piece_bag_default.copy()
        self.queue = []
        self.queue_size = queue_size
        self.update_queue()
        self.held_piece = None

        self.create_board_grid()

        self.piece = self.next_piece()

    def draw(self):
        ## Draws Held piece, board and queue.
        self.piece.draw()
        if self.show_shadow_piece:
            self.piece.draw_shadow_piece()

        if self.held_piece != None:
            self.held_piece.x = -5 * self.size + self.x
            self.held_piece.y = 0 + self.y
            self.held_piece.align()
            self.held_piece.draw()

        if not(self.hide_board):
            for y in range((self.height - self.invisible_layers) + 1):
                for x in range(self.width + 2):
                    if not isinstance(self.board_grid[self.invisible_layers + y][x],int):
                        self.board_grid[self.invisible_layers + y][x].draw()

        z = self.y
        for piece in self.queue:
            piece.x = self.x + (self.width + 2) * self.size 
            piece.y = z
            piece.align()
            piece.draw()
            z += self.size * 3

    def existent_square(self,x,y):
        ## Checks if a square in [x,y] exists.
        x = int(x/self.size - self.x/self.size)
        y = int(y/self.size - self.y/self.size)
        if x < 1 or x > self.width:
            return True
        elif y < 0:
            return False
        try:
            if self.board_grid[y][x] != 0:
                return True
            else:
                return False
        except:
            return False
    
    def lock_piece(self,piece):
        ## The function is called lock_piece since all the following events are caused by it.
        ## It might be better to call it something else and have lock_piece as an actual function
        #  that does what it is said to do. Could be useful for later on for freezing the board.
        ########
        ## Turn 'hold' on
        ## Locks piece's squares
        #
        ## Check if it is a possible T-spin
        ## Counts how many lines cleared
        ## Check if it is a combo, b2b, or combo-break
        #
        ## Deal damage, offset, or counter damage
        ## Takes damage based on a few rules
        #
        ## Check if top'ed out
        #########
        self.held = False ## Turn Hold on
        for square in piece.squares: ## Lock piece
            x = int(square.x/self.size - self.x/self.size)
            y = int(square.y/self.size - self.y/self.size)
            self.board_grid[y][x] = square
        
        lines_cleared = 0
        edges = 0
        if piece.piece == 'T': ## Checks if it is a T-spin
            for edge_x in [0,2]:
                for edge_y in [0,2]:
                    x,y = piece.x + edge_x * piece.size, piece.y + edge_y * piece.size
                    if self.existent_square(x,y):
                        edges += 1

        for y in range(self.height): ## Count how many lines cleared
            if self.clear_line(y):
                lines_cleared += 1
        self.align()

        if lines_cleared > 0: ## Count b2b and combo
            self.combo += 1
            if not((lines_cleared in [1,2,3] and edges >= 3) or (lines_cleared == 4)):
                self.btb = 0
            else:
                self.btb += 1
        else:
            self.combo = 0

        delta_dano = self.damage_queue - self.calculate_attack(lines_cleared,edges) ## Deal damage or clear damage queue
        if delta_dano < 0: ## If counter or attack
            if self.damage_queue == 0: ## If attack

                for opponent in self.opponents:
                    ball = self.create_attack_ball(
                        destinations=[[opponent.x + opponent.width * self.size/2,opponent.y]],
                        square=square,
                        function=lambda x=self.attack_opponents,y=-delta_dano : x(y))

                    self.attack_balls.append(ball)

            else: ## If counter

                for opponent in self.opponents:
                    destinations = [
                        [self.x + self.width * self.size/2,self.y],
                        [opponent.x + opponent.width * self.size/2,opponent.y]
                        ]
                    function = lambda x=self.attack_opponents,y=-delta_dano : x(y)
                    ball = self.create_attack_ball(destinations,square,function)

                    self.attack_balls.append(ball)

            self.damage_queue = 0

        elif self.calculate_attack(lines_cleared,edges) > 0: ## If offset

            destinations = [[self.x + self.width * self.size/2,self.y]]
            ball = AttackBall(
                        window=self.window,
                        destinations=destinations,
                        pointer=self.attack_balls,
                        function=None,
                        x=square.x,y=square.y
                        )
            self.attack_balls.append(ball)

            self.damage_queue = delta_dano

        if not(self.clear_avoids_damage and lines_cleared > 0):
            self.take_damage(min(self.damage_per_pass,self.damage_queue))
            self.damage_queue -= min(self.damage_per_pass,self.damage_queue)
        

    def reset_bag(self):
        self.bag = self.piece_bag_default.copy()
    
    def update_queue(self):
        if self.queue_size == 0:
            piece_type = self.bag.pop(random.randint(0,len(self.bag)-1))
            piece = Piece(self,self.window,piece_type,x=self.spawn_point[0],y=self.spawn_point[1],size=self.size,piece_syle=self.piece_style)
            return piece
        else:
            while len(self.queue) < self.queue_size:
                piece_type = self.bag.pop(random.randint(0,len(self.bag)-1))
                piece = Piece(self,self.window,piece_type,size=self.size,piece_syle=self.piece_style)
                self.queue.append(piece)
                if len(self.bag) == 0:
                    self.reset_bag()
    
    def next_piece(self):
        if self.queue_size == 0:
            n_p = self.update_queue()
            n_p.x = self.spawn_point[0]
            n_p.y = self.spawn_point[1]
            if len(self.bag) == 0:
                self.reset_bag()
        else:
            n_p = self.queue.pop(0)
            n_p.x = self.spawn_point[0]
            n_p.y = self.spawn_point[1]
            n_p.align()
            self.update_queue()
        
        return n_p
    
    def set_queue_size(self,new_size):
        while len(self.queue) > new_size:
            self.bag.append(self.queue.pop(0).piece)
        self.queue_size = new_size
        self.update_queue()
    

    def hold(self,piece):
        if self.held_piece == None:
            self.held_piece = piece
            self.reset_rotate(self.held_piece)
            self.held = True
            return self.next_piece()
        else:  
            piece_to_return = self.held_piece
            self.held_piece = piece
            piece_to_return.x = self.spawn_point[0] 
            piece_to_return.y = self.spawn_point[1] 
            piece_to_return.align()
            self.reset_rotate(self.held_piece)
            self.held = True
            return piece_to_return

    def reset_rotate(self,piece):
        while piece.rotation != 0:
            piece.rotate(-1)

    def hard_drop(self):
        self.piece.hard_drop()

    def movement(self):
        ## Sideways movement
        window_keyboard = self.window.keyboard
        controls = self.controls
        time_held = self.time_held
        settings = self.settings
        if window_keyboard.key_pressed(controls['right']) and not(window_keyboard.key_pressed(controls['left'])):
            if time_held['right'] == 0:
                self.piece.move_x(1)
            elif time_held['right'] > settings['DAS']['time']:
                time_held['right_das'] += self.window.delta_time()
                if time_held['right_das'] > settings['DAS']['speed']:
                    time_held['right_das'] -= settings['DAS']['speed']
                    self.piece.move_x(1)
            time_held['right'] += self.window.delta_time()
        else:
            time_held['right'] = 0
            time_held['right_das'] = 0

        if window_keyboard.key_pressed(controls['left']) and not(window_keyboard.key_pressed(controls['right'])):
            if time_held['left'] == 0:
                self.piece.move_x(-1)
            elif time_held['left'] > settings['DAS']['time']:
                time_held['left_das'] += self.window.delta_time()
                if time_held['left_das'] > settings['DAS']['speed']:
                    time_held['left_das'] -= settings['DAS']['speed']
                    self.piece.move_x(-1)
            time_held['left'] += self.window.delta_time()
        else:
            time_held['left'] = 0
            time_held['left_das'] = 0
        
        ## Rotation
        if window_keyboard.key_pressed(controls['rotate_l']) and not(time_held['rotate_l']):
            self.piece.rotate(-1)
            time_held['rotate_l'] = 1
        elif not(window_keyboard.key_pressed(controls['rotate_l'])):
            time_held['rotate_l'] = 0

        if window_keyboard.key_pressed(controls['rotate_r']) and not(time_held['rotate_r']):
            self.piece.rotate(1)
            time_held['rotate_r'] = 1
        elif not(window_keyboard.key_pressed(controls['rotate_r'])):
            time_held['rotate_r'] = 0

        ## Soft drop, harddrop, gravity
        if window_keyboard.key_pressed(controls['soft_drop']):
            self.piece.move_y(self.piece.size * self.window.delta_time() * 1.2)

        if window_keyboard.key_pressed(controls['hard_drop']) and time_held['hard_drop'] == 0:
            self.hard_drop()
            time_held['hard_drop'] = 1
        elif not window_keyboard.key_pressed(controls['hard_drop']):
            time_held['hard_drop'] = 0

        self.piece.move_y(self.piece.size * self.window.delta_time() * self.gravity)

        ## Hold
        if window_keyboard.key_pressed(controls['hold']) and time_held['hold'] == 0 and not(self.held):
            self.piece = self.hold(self.piece)
            time_held['hold'] = 1
        elif not(window_keyboard.key_pressed(controls['hold'])):
            time_held['hold'] = 0

        if self.piece.stalling_timer > self.piece.max_staling_time or self.piece.stalled >= self.piece.max_staling_amount:
            self.lock_piece(self.piece)
            self.piece = self.next_piece()


    def align(self):
        x = self.x
        y = self.y
        for row in self.board_grid:
            x = self.x
            for col in row:
                if col != 0:
                    col.x = x
                    col.y = y
                x += self.size
            y += self.size

    
    def empty_row(self):
        return [Square(solid_color,style=self.piece_style,solid=1,size=self.size)] + [0] * self.width + [Square(solid_color,style=self.piece_style,solid=1,size=self.size)]
            
    def damage_row(self,hole):
        """hole -> [1,10]"""
        row = [Square(solid_color,size=self.size,solid=1)]  ## solid

        for _ in range(0,hole):
            row.append(Square(damage_color,size=self.size)) ## damage

        row.append(0)                                        ## empty

        for _ in range(hole+1,10):
            row.append(Square(damage_color,size=self.size)) ## damage

        row.append(Square(solid_color,solid=1,size=self.size)) ## solid

        return row


    def clear_line(self,height):
        for x in range(self.width):
            if self.board_grid[height][x+1] == 0:
                return False
            elif self.board_grid[height][x+1].solid == 1:
                return False
        self.board_grid.pop(height)
        self.board_grid.insert(0,self.empty_row())
        return True

    def take_damage(self,amount,irregularity=(0,0)):
        for _ in range(amount):
            self.board_grid.insert(-1,self.damage_row(2))
            self.board_grid.pop(0)
        self.align()
    
    def calculate_attack(self,lines_cleared,edges):
        if edges == 3:
            if lines_cleared == 1:
                return 2 + (self.btb > 1)
            elif lines_cleared == 2:
                return 4 + (self.btb > 1)
            elif lines_cleared == 3:
                return 5 + (self.btb > 1)
        if lines_cleared > 0:
            return lines_cleared + (self.btb > 1)
        else:
            return 0
    
    def attack_opponents(self,damage):
        for opponent in self.opponents:
            opponent.damage_queue += damage

    def attack_message(self,lines_cleared,edges):
        if lines_cleared > 0:
            message = ""
            if self.btb > 0:
                message += 'Back-to-Back '
            if lines_cleared == 1 and edges >= 3:
                message += ("T-spin Single ")
            elif lines_cleared == 2 and edges >= 3:
                message += ("T-spin Double ")
            elif lines_cleared == 3 and edges >= 3:
                message += ("T-spin Triple ")
            elif lines_cleared == 4:
                message += ("Tetris!")
            else:
                message = (str(lines_cleared) + " lines cleared")
                return message, 'Combo ' + str(self.combo) + "x!"

            if self.btb > 1:
                return message + "x" + str(self.btb), 'Combo ' + str(self.combo) + "x!"
            else:
                return message, 'Combo ' + str(self.combo) + "x!"
    
    def create_attack_ball(self,destinations,square,function=None):
        ball = AttackBall(
                        window=self.window,
                        pointer=self.attack_balls,
                        destinations=destinations,
                        function=function,
                        x=square.x,y=square.y
                        )
        return ball
        
    def create_board_grid(self):
        self.board_grid = []

        for _ in range(self.height):
            self.board_grid.append(self.empty_row())
        last_row = [] ## All solids
        for _ in range(self.width + 2):
            last_row.append(Square(solid_color,style=self.piece_style,solid=1,size=self.size))

        self.board_grid.append(last_row)
        self.align()