import pygame
import sys
from os import path
import time
import random

WIDTH = 400
HEIGHT = 500
AGENT_RADIUS = 15
PIPE_WIDTH = 53

horizontal_speed = 5
gravity_value = 12
flap_value = 50
gap = 95                         # Gap between pipes
gap_btw_horizontal_pipe = 200

file_path = path.abspath(__file__)  # full path of main.py
dir_path = path.dirname(file_path)  # full path of the directory
bg_jpg = path.join(dir_path, 'resources/download.png')  # absolute background image path
agent_jpg = path.join(dir_path, 'resources/bird.png')
pipe_jpg = path.join(dir_path, 'resources/pipe.png')
# retro_font = path.join(dir_path, 'retro.ttf')  # absolute font path


def move_y_axis(agent, switch=0):
    if switch == 0: # gravity case default
        y = agent[1]
        y += gravity_value
        return (agent[0], y)
    else:           # flap
        y = agent[1]
        y -= flap_value
        return (agent[0], y)

class Pipe:
    def __init__(self, win, x_axis, pg):
        self.width = PIPE_WIDTH
        self.x_axis = x_axis

        self.pg = pg
        self.pg1 = pg
        self.pg2 = pg
        self.constructor()
        self.win = win
        

    def constructor(self):
        self.height = random.choice(range(30, HEIGHT - (gap + 30))) # HEight of upper pipe
        self.height_inverse = HEIGHT - (self.height+ gap)
        self.rect = pygame.Rect(self.x_axis, 0, PIPE_WIDTH, self.height)
        self.rect_inverse = pygame.Rect(self.x_axis, HEIGHT - self.height_inverse, PIPE_WIDTH, self.height_inverse)

        self.pg2 = pygame.transform.rotate(self.pg, 180)
        self.pg2 = pygame.transform.scale(self.pg2, (PIPE_WIDTH, self.height_inverse))
        self.pg1 = pygame.transform.scale(self.pg, (PIPE_WIDTH, self.height))

    def show(self):
        pygame.draw.rect(self.win, (50,205,50), self.rect)
        pygame.draw.rect(self.win, (50,205,50), self.rect_inverse)
        self.win.blit(self.pg1, self.rect)
        self.win.blit(self.pg2, self.rect_inverse)

    def move(self):
        self.rect.move_ip([-horizontal_speed, 0])
        self.rect_inverse.move_ip([-horizontal_speed, 0])
        self.show()

    def manage_pipe(self):
        self.move()
        if self.rect[0] <= (-PIPE_WIDTH):
            self.x_axis = WIDTH
            self.constructor()
            self.show()

def collision_detection(agent_rect, pp1, pp2):
    if agent_rect[1] >= HEIGHT:
        return True
    elif agent_rect[1] <= 0:
        return True
    for i in [pp1, pp2]:
        for j in i:
            if agent_rect.colliderect(j):
                return True

    return False


def game_window():
    """Game window"""
    while True:
        run = True
        win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy bird")
        bg = pygame.image.load(bg_jpg)
        bg = pygame.transform.scale(bg, (WIDTH+300, HEIGHT))
        ag = pygame.image.load(agent_jpg)
        ag = pygame.transform.scale(ag, (AGENT_RADIUS*2.5, AGENT_RADIUS*2))
        pg = pygame.image.load(pipe_jpg)

        agent = (WIDTH/2, HEIGHT/2) # agent center
        user_click = False
        pp = Pipe(win, (WIDTH ), pg)
        pp2 = Pipe(win, ((WIDTH ) +  gap_btw_horizontal_pipe), pg)

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    user_click = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        user_click = True
                if user_click == True:
                    user_click = False
                    agent = move_y_axis(agent, switch="flap")

            
            agent_Rect = pygame.draw.circle(win, (255,255,0), agent, AGENT_RADIUS) # will use agent(center) to manipulate position and agent_rect to only check for collisions
            agent = move_y_axis(agent)

            win.blit(bg, (0, 0)) # TODO impliment moving img effect as x axis moves
            win.blit(ag, agent_Rect)
      
            pp.manage_pipe()
            pp2.manage_pipe()
            pygame.display.update()
            
            if collision_detection(agent_Rect, [pp.rect, pp.rect_inverse], [pp2.rect, pp2.rect_inverse]):
                print("You lost")
          #      time.sleep(3)

            time.sleep(0.1)

if __name__ == '__main__':
    game_window()
