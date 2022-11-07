import pygame
import sys
from os import path
import time
import random
import neat
pygame.font.init()

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
retro_font = path.join(dir_path, 'resources/retro.ttf')  # absolute font path

score = -1

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
        global score
        score += 1

    def show(self):
        pygame.draw.rect(self.win, (50,205,50), self.rect)
        pygame.draw.rect(self.win, (50,205,50), self.rect_inverse)
        self.win.blit(self.pg1, self.rect)
        self.win.blit(self.pg2, self.rect_inverse)

    def move(self):
        self.rect.move_ip([-horizontal_speed, 0])
        self.rect_inverse.move_ip([-horizontal_speed, 0])
        self.show()

    def manage_pipe(self, gef=[0,[]]):
        self.move()
        if self.rect[0] <= (-PIPE_WIDTH):
            self.x_axis = WIDTH
            self.constructor()
            self.show()
            if gef[0] != 0:
                for g in gef[1]:
                    g.fitness += 5
        return gef[1]

class Bird:
    def __init__(self, win, x, y):
        self.x =  x
        self.y = y
        self.rect = []
        self.win = win

    def move_y_axis(self, switch=0):
        if switch == 0: # gravity case default
            self.y += gravity_value
        else:           # flap
            self.y -= flap_value

    def manage(self, ag, bg):
        self.move_y_axis()
#        self.rect = pygame.draw.circle(self.win, (255,255,0), (self.x, self.y), AGENT_RADIUS) # will use agent(center) to manipulate position and agent_rect to only check for collisions
        self.rect = pygame.Rect(self.x, self.y, AGENT_RADIUS, AGENT_RADIUS)
#        self.win.blit(bg, (0, 0)) # impliment moving img effect as x axis moves
        self.win.blit(ag, self.rect)


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

def game_window(genomes, config):
    """Game window"""
    
    run = True
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy bird")
    bg = pygame.image.load(bg_jpg)
    bg = pygame.transform.scale(bg, (WIDTH+300, HEIGHT))
    ag = pygame.image.load(agent_jpg)
    ag = pygame.transform.scale(ag, (AGENT_RADIUS*2.5, AGENT_RADIUS*2))
    pg = pygame.image.load(pipe_jpg)
    font = pygame.font.Font(retro_font, 30)
    pp = Pipe(win, (WIDTH ), pg)
    pp2 = Pipe(win, ((WIDTH ) +  gap_btw_horizontal_pipe), pg)
    pipe_cur = pp

    agent = Bird(win, WIDTH/2, HEIGHT/2) # agent center

    agents = []
    nets = []
    ge = []
    for x,g in genomes:
        g.fitness = 0   
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        agents.append(Bird(win, WIDTH/2, HEIGHT/2))
        ge.append(g)

    while run and len(agents) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
        for x,agent in enumerate(agents):
            output = nets[x].activate((abs(agent.y), abs(agent.y - pipe_cur.rect[1]), abs(agent.y - pipe_cur.rect_inverse[1])))
            if output[0] > 0.5:
                agent.move_y_axis(switch="flap")

        win.blit(bg, (0, 0)) # impliment moving img effect as x axis moves
        for agent in agents: 
            agent.manage(ag, bg)

        label = font.render(f"Score : {score}", 1, (255,165,0))
        win.blit(label, (0, 0))
    
        ge = pp.manage_pipe(gef=[1,ge])
        ge = pp2.manage_pipe(gef=[0,ge])
        pygame.display.update()

        pipe_cur = pp
        if len(agents) > 0 and agents[0].x > (pipe_cur.rect[0] + pipe_cur.width):
            pipe_cur = pp2

        for x, agent in enumerate(agents):
            if collision_detection(agent.rect, [pp.rect, pp.rect_inverse], [pp2.rect, pp2.rect_inverse]):
                ge[x].fitness -= 1 # encourage not hittin pipes
                agents.pop(x)
                nets.pop(x)
                ge.pop(x)

        time.sleep(0.1)

def runner(config):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config)
    popul = neat.Population(config)

    # show progress in the terminal
    popul.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    popul.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    winner = popul.run(game_window, 10) # 50 to> 1

if __name__ == '__main__':
    print("Neat")
    config_path = path.join(dir_path, 'config.txt')
    runner(config_path)
