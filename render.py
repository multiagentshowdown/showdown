import pygame
import time
import random
from math import ceil, floor

SAMPLE_COLORS = True
# colors
GROUND_C = (246, 169, 125)
WALL_C = (235, 116, 86)
WATER_C = (31, 152, 223)
AGENT_C = [(230, 25, 75), (245, 130, 48), (255, 225, 25), (60, 180, 75), \
           (0, 0 , 128), (145, 30, 180), (240, 50, 230), (128, 128, 128)]
if SAMPLE_COLORS:
    AGENT_C = random.sample(AGENT_C, len(AGENT_C))
BULLET_C = []
for i in range(0, len(AGENT_C)):
    color = []
    for element in AGENT_C[i]:
        color.append(element * 3/4)
    BULLET_C.append(tuple(color))

terrain_dict = {0: 'GROUND', 1: 'WALL', 2: 'WATER'}

class window:
    def __init__(self, _scale, _dim):
        pygame.init()
        self.scale = _scale
        self.screen = pygame.display.set_mode((_dim[0] * self.scale,
        _dim[1] * self.scale))
        pygame.display.set_caption('showdown')
    def render(self, env, delay=0.25):
        pygame.draw.rect(self.screen, GROUND_C, [0, 0, env.height*self.scale, \
        env.width*self.scale])
        for h in range(0, env.height):
            for w in range(0, env.width):
                if terrain_dict[env.map[h, w]] == 'WALL':
                    pygame.draw.rect(self.screen, WALL_C, [self.scale * h, \
                    self.scale * w, self.scale, self.scale])
                elif terrain_dict[env.map[h, w]] == 'WATER':
                    pygame.draw.rect(self.screen, WATER_C, [self.scale * h, \
                    self.scale * w, self.scale, self.scale])
        agent_overlap = []
        bullet_overlap = []
        for key_a, agent in env.agents.items():
            pygame.draw.circle(self.screen, AGENT_C[key_a], [int(agent.loc.c \
            * self.scale + ceil(self.scale/2)), int(agent.loc.r * self.scale \
            + ceil(self.scale/2))], ceil(self.scale*0.3))
            if agent.loc.tuple() in agent_overlap:
                pygame.draw.circle(self.screen, (255,255,255), [int(agent.loc.c \
                * self.scale + ceil(self.scale/2)), int(agent.loc.r * self.scale \
                + ceil(self.scale/2))], ceil(self.scale*0.3))
            else:
                agent_overlap.append(agent.loc.tuple())
            for key_b, bullet in env.agents[key_a].bullets.items():
                pygame.draw.circle(self.screen, BULLET_C[key_a], [int(bullet.loc.c \
                * self.scale + ceil(self.scale/2)), int(bullet.loc.r \
                * self.scale + ceil(self.scale/2))], ceil(self.scale*0.2))
                if bullet.loc.tuple() in bullet_overlap:
                    pygame.draw.circle(self.screen, (255,255,255), [int(bullet.loc.c \
                    * self.scale + ceil(self.scale/2)), int(bullet.loc.r \
                    * self.scale + ceil(self.scale/2))], ceil(self.scale*0.2))
                else:
                    bullet_overlap.append(bullet.loc.tuple())
        pygame.display.update()
        time.sleep(delay)
