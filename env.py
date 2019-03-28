from helper import *
import pandas as pd
import numpy as np
import random

GROUND = 0
WATER = 2
WALL = 1
MAX_BULLETS = 3
RELOAD_SPEED = 1
NUM_TERRAIN = 3

terrain_dict = {0: 'GROUND', 1: 'WALL', 2: 'WATER'}

class action:
    def __init__(self, _type, _dir, _enc):
        self.type = _type
        self.dir = _dir
        self.enc = self.encode()
    def encode(self):
        count = 0
        for type in ['MOVE', 'SHOOT']:
            for dir in ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'none']:
                if type == self.type and dir == self.dir:
                    return count
                else:
                    count += 1
        print('Something went wrong! Action is not valid.')
        quit()

action_dict = { 0: action('MOVE', 'n', 0),
                1: action('MOVE', 'ne', 1),
                2: action('MOVE', 'e', 2),
                3: action('MOVE', 'se', 3),
                4: action('MOVE', 's', 4),
                5: action('MOVE', 'sw', 5),
                6: action('MOVE', 'w', 6),
                7: action('MOVE', 'nw', 7),
                8: action('MOVE', 'none', 8),
                9: action('SHOOT', 'n', 9),
                10: action('SHOOT', 'ne', 10),
                11: action('SHOOT', 'e', 11),
                12: action('SHOOT', 'se', 12),
                13: action('SHOOT', 's', 13),
                14: action('SHOOT', 'sw', 14),
                15: action('SHOOT', 'w', 15),
                16: action('SHOOT', 'nw', 16)}

dir_dict = {'n': loc(-1,0),
            'ne': loc(-1,1),
            'e': loc(0,1),
            'se': loc(1,1),
            's': loc(1,0),
            'sw': loc(1,-1),
            'w': loc(0,-1),
            'nw': loc(-1,-1),
            'none': loc(0,0)}

obs_dict = {'raw_pix': 0,
            'one_hot': 1}

class bullet:
    def __init__(self, _loc, _dir):
        self.loc = _loc
        self.dir = _dir
    def step(self):
        print(self.loc)
        print(self.dir)
        self.loc =  self.loc + self.dir

class agent():
    def __init__(self, _loc, _id, _user=False):
        self.loc = _loc
        self.id = _id
        self.user = _user
        self.bullets = {}
        self.bullet_count = MAX_BULLETS
        self.index = 0
        self.is_dead = False
    def step(self, map, a_idx):
        a = action_dict[a_idx]
        # re'MOVE', 'bullet(s) which collide with WALL
        del_keys = []
        for key, value in self.bullets.items():
            # update bullets[key]
            self.bullets[key].step()
            index = self.bullets[key].loc
            if map[index.r, index.c] == WALL:
                del_keys.append(key)
        for key in del_keys:
            del self.bullets[key]
        if self.loc != loc(-1,-1):
            # step current action
            if a.type == 'SHOOT':
                bullet_loc = self.loc + dir_dict[a.dir]
                self.bullets[self.index] = bullet(bullet_loc, dir_dict[a.dir])
                self.index += 1
                self.bullet_count -= 1
                if self.bullet_count < 0:
                    print('Something went wrong! Bullet count < 0.')
                    quit()
                else:
                    None
            elif a.type == 'MOVE':
                self.loc = self.loc + dir_dict[a.dir]
            else:
                None
        else:
            None
    def reload(self):
        self.bullet_count = max(self.bullet_count+1, MAX_BULLETS)


class Env():
    def __init__(
            self,
            _num_agents,
            _map,
            _dim,
            _loc_dict=None,
            _user=None,
            _obs_type=None):
        print('Creating an environment...')
        print('Reading %s.txt...' % (_map))
        self.height, self.width = _dim
        self.terrain = np.zeros((NUM_TERRAIN-1,self.height,self.width))
        self.map = np.zeros((self.height,self.width))
        for i in range(1, NUM_TERRAIN):
            self.terrain[i-1,:,:] += pd.read_csv(_map + '_' + terrain_dict[i] + '.txt', header=None).values
            self.map += i * self.terrain[i-1,:,:]
        print('Height: %s; Width: %s' % (str(self.height), str(self.width)))
        self.num_agents = _num_agents
        print('Number of agents: %s' % (str(self.num_agents)))
        self.obs_type = _obs_type
        print('Observation type: %s' % (_obs_type))
        if _loc_dict is None:
            locs = []
            loc_dict = {}
            for i in range(0, self.num_agents):
                r, c = 0, 0
                while terrain_dict[self.map[r,c]] != 'GROUND' or loc(r,c) in locs:
                    r = random.randint(0, self.height-1)
                    c = random.randint(0, self.width-1)
                locs.append(loc(r,c))
                loc_dict[i] = loc(r,c)
        else:
            loc_dict = _loc_dict
        if _user is not None:
            if _user >= 0 and _user < self.num_agents:
                self.user = _user
            else:
                print('Something went wrong! User id is out of range.')
                self.user = None
        else:
            self.user = _user
        self.agents = {}
        # instantiate all agents
        for i in range(0, self.num_agents):
            self.agents[i] = agent(loc_dict[i], i, self.user==i)
            print('Added Agent %s at %s' % (str(i), self.agents[i].loc))
        self.time = 0
        self.alive = np.arange(0, self.num_agents)
    def step(self, action_list):
        for i in range(0, self.num_agents):
            self.agents[i].step(self.map, action_list[i])
            if self.time % RELOAD_SPEED == 0:
                self.agents[i].reload()
        self.time += 1
    def is_valid(self, index, source):
        a = action_dict[index]
        dest = source + dir_dict[a.dir]
        if a.type == 'MOVE':
            if terrain_dict[self.map[dest.r, dest.c]] == 'GROUND':
                return True
            else:
                return False
        elif a.type == 'SHOOT':
            if terrain_dict[self.map[dest.r, dest.c]] == 'GROUND' or \
            terrain_dict[self.map[dest.r, dest.c]] == 'WATER':
                return True
            else:
                return False
        else:
            print('Invalid action type.')
    def action_space(self, agent_id):
        source = self.agents[agent_id].loc
        valid_actions = []
        for i in range(0, len(action_dict)):
            append = self.is_valid(i, source)
            if append:
                valid_actions.append(i)
            else:
                None
        return valid_actions
    def observation(self):
        if obs_dict[self.obs_type] == 0:
            return None
        elif obs_dict[self.obs_type] == 1:
            obs = np.zeros((self.num_agents * 2 + NUM_TERRAIN-1, self.height, self.width))
            for a_key, a in self.agents.items():
                obs[a_key, a.loc.r, a.loc.c] = 1
                for b_key, b in self.agents[a_key].bullets.items():
                    obs[self.num_agents + a_key, b.loc.r, b.loc.c] = 1
            for i in range(1, NUM_TERRAIN):
                obs[self.num_agents * 2 + (i - 1),:,:] = self.terrain[i-1,:,:]
            return obs.astype(int)
    def reward(self):
        reward = []
        agents = []
        bullets = []
        for key_a, a in self.agents.items():
            agents.append(a.loc.tuple())
            for key_b, b in self.agents[key_a].bullets.items():
                bullets.append(b.loc.tuple())
        print(agents)
        print(bullets)
        common = (set(agents) & set(bullets))
        for i in range(0, len(agents)):
            if len(self.alive) == 1:
                print('Agent %s is the winner!' % (str(i)))
                quit()
            elif agents[i] in common:
                self.alive = np.delete(self.alive, i)
                self.agents[i].is_dead = True
                self.agents[i].loc = loc(-1,-1)
                reward.append(-1)
            elif agents[i] == (-1,-1):
                reward.append(0)
            else:
                reward.append(0)
