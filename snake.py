import pygame
import torch
import math
from sys import argv

from random import randint
from model import model, train_step, path

WIDTH = 800
HEIGHT = 800
FPS = 60

DEBUG  =  True
SHOULD_LEARN =  False
NOMODEL = False

BACKGROUND_COLOR = (64, 128, 64)
FOREGROUND_COLOR = (0, 192, 0)

class Direction:
    LEFT    =  0
    RIGHT   =  1
    UP      =  2
    DOWN    =  3
    
    def reverse(dir):
        match dir:
            case Direction.LEFT:
                return Direction.RIGHT
            
            case Direction.UP:
                return Direction.DOWN
            
            case Direction.DOWN:
                return Direction.UP
            
            case Direction.RIGHT:
                return Direction.LEFT
            
    def move(vec, dir):
        match dir:
            case Direction.RIGHT:
                return [vec[0] + 1, vec[1]]
            case Direction.LEFT:
                return [vec[0] - 1, vec[1]]
            case Direction.UP:
                return  [vec[0], vec[1] - 1]
            case Direction.DOWN:
                return  [vec[0], vec[1]  +  1]
            
    def print(dir):
        match dir:
            case Direction.RIGHT:
                return "Right"
            case Direction.LEFT:
                return "Left"
            case Direction.UP:
                return "Up"
            case Direction.DOWN:
                return "Down"
       
 

class Field:
    width = WIDTH - 100 
    height = HEIGHT - 100
    
    x =  int((WIDTH - width) / 2)
    y =  int((HEIGHT  - height)  / 2)
    
    cell_count = 20
    cell_size = (width / cell_count, height / cell_count)
    
    head_color = (0, 255, 255)
    body_color = (0, 200, 200)
    
    apple = [6, 6]
    
    def __init__(self):
        Field.apple = [randint(0, Field.cell_count - 1), randint(0, Field.cell_count - 1)]
        self.snake = Field.Snake(Direction.RIGHT)
    ### Init
        
    def move(self):
        val = self.snake.move()
        return val
    ### Move

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 160, 0),  (Field.x, Field.y, Field.width, Field.height))
        self.snake.draw(screen)
        pygame.draw.rect(screen, (255, 0, 0), (Field.x + Field.apple[0] * Field.cell_size[0], Field.y + Field.apple[1]* Field.cell_size[1], Field.cell_size[0], Field.cell_size[1]))
        return
    ### Draw
        
    class Snake:
        class Body:
            def __init__(self, x, y):
                self.x  =  x
                self.y  =  y
            ### Init
        ### Body
        
        def __init__(self, direction):
            self.body = []
            self.direction = direction
            
            base = [5, 5]
            self.body.append(Field.Snake.Body(base[0], base[1]))
            
            base = Direction.move(base, Direction.reverse(direction))
            self.body.append(Field.Snake.Body(base[0], base[1]))
            
            base = Direction.move(base, Direction.reverse(direction))
            self.body.append(Field.Snake.Body(base[0], base[1]))
            
            self.queued_move = -1
            self.should_move = True
            
        ### Init
        
        def draw(self, screen):
            screen.fill(Field.head_color, (Field.x + self.body[0].x * Field.cell_size[0], Field.y + self.body[0].y * Field.cell_size[1], Field.cell_size[0], Field.cell_size[1]))
            texture=pygame.image.load("pic.jpg")
            screen.blit(texture, (Field.x + self.body[0].x * Field.cell_size[0], Field.y + self.body[0].y * Field.cell_size[1], Field.cell_size[0], Field.cell_size[1]))
            
            for i in range(1, len(self.body)):
                screen.fill(Field.body_color, (Field.x + self.body[i].x * Field.cell_size[0], Field.y + self.body[i].y * Field.cell_size[1], Field.cell_size[0], Field.cell_size[1]))
        ### draw
        
        def move(self):
            if self.queued_move != -1:
                self.direction = self.queued_move
                self.queued_move = -1
            self.should_move = True    
                
            for i in range(0, len(self.body) - 1):
                self.body[len(self.body) - i - 1].y =  self.body[len(self.body) - i - 1 - 1].y
                self.body[len(self.body) - i - 1].x =  self.body[len(self.body) - i - 1 - 1].x
                
                if self.body[i].x < 0 or self.body[i].y < 0 or self.body[i].x == Field.cell_count or self.body[i].y == Field.cell_count:
                    return -1
                
            moved = Direction.move([self.body[0].x, self.body[1].y], self.direction)
            
            self.body[0].x =  moved[0]
            self.body[0].y =  moved[1]
                
            if self.body[0].x < 0 or self.body[0].y < 0 or self.body[0].x == Field.cell_count or self.body[0].y == Field.cell_count:
                return -1
            
            for i in range(1, len(self.body)):
                if self.body[i].x == self.body[0].x  and  self.body[i].y  ==  self.body[0].y:
                    return -1

            if self.body[0].x == Field.apple[0]  and  Field.apple[1]  ==  self.body[0].y:
                self.add_body()
                Field.apple = [randint(0, Field.cell_count - 1), randint(0, Field.cell_count - 1)]
                return 1
                        
            return 0
        ### move
        
        def add_body(self):
            pos = Direction.move([self.body[len(self.body) - 1].x, self.body[len(self.body) - 1].y], Direction.reverse(self.direction))
            self.body.append(Field.Snake.Body(pos[0], pos[1]))
        ### add body
        
        def change_direction(self, direction):
            if self.should_move:
                self.queued_move = direction
                self.should_move  = False
        ### change_direction
        
        def get_direction(self):
            return self.direction
        ### change_direction
        
        def cast_rays(self):
            res = []
            
            res.append(self.cast_to(Direction.LEFT))
            res.append(self.cast_to(Direction.RIGHT))
            res.append(self.cast_to(Direction.UP))
            res.append(self.cast_to(Direction.DOWN))
            
            return res
                    
        def cast_to(self, direction):
            res = 0
            startpos  =  [ self.body[0].x, self.body[0].y]
            while (startpos[0] < Field.cell_count and startpos[0] >= 0 and startpos[1] >= 0 and startpos[1] < Field.cell_count):
                
                for i in range(1, len(self.body)):
                    if self.body[i].x  ==  startpos[0] and self.body[i].y == startpos[1]:
                        return res
                    
                startpos = Direction.move(startpos, direction)
                res += 1
                
            return res
            
        ### cast
            
    ### Snake
### Field
        
        
def distance_head_apple(field):
    return math.sqrt((Field.apple[0] - field.snake.body[0].x)**2 + (Field.apple[1] - field.snake.body[0].y)**2)
        
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    clock = pygame.time.Clock()
    
    SHOULD_LEARN = False
    BASE_SPEED = 0
    NOMODEL = False
    
    print(argv)
    for i in range(0, len(argv)):
        match argv[i]:
            case "--train":
                SHOULD_LEARN = True
                print("training flag")
            case "--speed":
                try:
                    BASE_SPEED = int(argv[i + 1])
                    print(f"speed flag. speed = {BASE_SPEED}")
                except IndexError:
                    print("Did not recognize the speed")
            case "--nomodel":
                NOMODEL = True
        
    
    field =  Field()
    counter = 0
    speed = BASE_SPEED
    
    
    if not NOMODEL:
        try:
            model.load_state_dict(torch.load(path))
        except FileNotFoundError:
            pass

        rays = field.snake.cast_rays()
        data = [Field.apple[0], Field.apple[1], field.snake.body[0].x, field.snake.body[0].y, rays[0], rays[1], rays[2], rays[3], Field.cell_count, Field.cell_count, len(field.snake.body), field.snake.direction, distance_head_apple(field)]
        data = torch.tensor(data, dtype=torch.float32)
        data = model(data)
        print(data)
        
        print(torch.argmax(data))
    
    record = 0
    collected = 0
    death_counter = 0
    
    running = True
    while running:
        if speed == 1000000:
            field = None
            field = Field()
            speed = BASE_SPEED
            counter = 0
            continue
            
            
        got_apple = 0
        died = 0
        
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type  ==  pygame.KEYDOWN:
                
                match event.key:
                    case pygame.K_RIGHT:
                        if field.snake.get_direction() != Direction.reverse(Direction.RIGHT):
                            field.snake.change_direction(Direction.RIGHT)
                        
                    case pygame.K_LEFT:
                        if field.snake.get_direction() != Direction.reverse(Direction.LEFT):
                            field.snake.change_direction(Direction.LEFT)
                        
                    case pygame.K_UP:
                        if field.snake.get_direction() != Direction.reverse(Direction.UP):
                            field.snake.change_direction(Direction.UP)
                        
                    case pygame.K_DOWN:
                        if field.snake.get_direction() != Direction.reverse(Direction.DOWN):
                            field.snake.change_direction(Direction.DOWN)
                        
                    case pygame.K_ESCAPE:
                        running  = False
                        
                    case pygame.K_SPACE:
                        field.snake.add_body()
                        
                    case pygame.K_LCTRL:
                        print(field.snake.cast_rays())
    
        
        if counter == speed:
            if not NOMODEL:
                distance_before_move = distance_head_apple(field)
                rays = field.snake.cast_rays()
                data = [Field.apple[0], Field.apple[1], field.snake.body[0].x, field.snake.body[0].y, rays[0], rays[1], rays[2], rays[3], Field.cell_count, Field.cell_count, len(field.snake.body), field.snake.direction, distance_before_move]
                state = data
                state = torch.tensor(state, dtype=torch.float32)
                
                result = model(state)
                #print(result)
                move = torch.argmax(result)
                
                match move:
                    case Direction.LEFT:
                        if field.snake.get_direction() != Direction.reverse(Direction.LEFT):
                            field.snake.change_direction(Direction.LEFT)
                    case Direction.RIGHT:
                        if field.snake.get_direction() != Direction.reverse(Direction.RIGHT):
                            field.snake.change_direction(Direction.RIGHT)
                    case Direction.UP:
                        if field.snake.get_direction() != Direction.reverse(Direction.UP):
                            field.snake.change_direction(Direction.UP)
                    case Direction.DOWN:
                        if field.snake.get_direction() != Direction.reverse(Direction.DOWN):
                            field.snake.change_direction(Direction.DOWN)
            
                print(f"Record: {record}\t Deaths: {death_counter}\t Current: {collected} \t argmax = {torch.argmax(result)} \t maxval = {torch.max(result)}")

            res = field.move()
            counter = 0
            if res == -1:
                speed = 1000000
                counter = 0
                died = -0.05
                collected = 0
                death_counter += 1
            elif res ==  1:
                got_apple =  1
                collected += 1
                
            
            if SHOULD_LEARN and not NOMODEL:
                distance_after_move = distance_head_apple(field)
                rays = field.snake.cast_rays()
                next_data = [Field.apple[0], Field.apple[1], field.snake.body[0].x, field.snake.body[0].y, rays[0], rays[1], rays[2], rays[3], Field.cell_count, Field.cell_count, len(field.snake.body), field.snake.direction, distance_after_move]
                next_state = torch.tensor(next_data, dtype=torch.float32)
                    
            #print(f'Before = {distance_before_move} ; After = {distance_after_move}')
                    
                if got_apple ==  1:
                    train_step(state, move, 1, next_state, True)
                    got_apple  =  0
                    
                elif died  != 0:
                    train_step(state, move, -1, next_state, False)
                    
                elif math.fabs(distance_before_move) <  math.fabs(distance_after_move):
                    train_step(state, move, -0.1, next_state, False)
                    
                elif math.fabs(distance_before_move) >  math.fabs(distance_after_move):
                    train_step(state, move, 0.1, next_state, False)
                    
                else:
                    train_step(state, move, 0.00001, next_state, False)
        else:
            counter += 1
            
        # 
            
        if collected >= record:
            record = collected
            
            
        screen.fill(BACKGROUND_COLOR)
        field.draw(screen)
        
        pygame.display.flip()
                
    pygame.quit()
    if not NOMODEL:
        torch.save(model.state_dict(), path)

if __name__ == "__main__":
    main()
    
