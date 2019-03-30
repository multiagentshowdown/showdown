from helper import *
import pandas as pd
import numpy as np
import random
import pickle

# CONSTANTS
# maximum bullet capacity
MAX_BULLETS = 1
# number of turns per bullet reload
RELOAD_SPEED = 1
# number of terrain features (including GROUND)
NUM_TERRAIN = 3
# terrain dictionary
terrain_dict = {0: 'GROUND', 1: 'WALL', 2: 'WATER'}

class Action:
    """
    This class is used to describe an action.

    Attributes:
        type: The type of an action.
        dir: The direction or trajectory of an action.
        enc: The encoding of an action to convert back to an integer.
    """
    def __init__(self, _type, _dir, _enc):
        """
        The constructor for Action class.
        """
        self.type = _type
        self.dir = _dir
        self.enc = _enc
    def __str__(self):
        return '%s %s' % (self.type, self.dir)
    def __repr__(self):
        return '%s %s' % (self.type, self.dir)

# conversion between Action class and its corresponding integer encoding
action_dict = { 0: Action('MOVE', 'n', 0),
                1: Action('MOVE', 'ne', 1),
                2: Action('MOVE', 'e', 2),
                3: Action('MOVE', 'se', 3),
                4: Action('MOVE', 's', 4),
                5: Action('MOVE', 'sw', 5),
                6: Action('MOVE', 'w', 6),
                7: Action('MOVE', 'nw', 7),
                8: Action('MOVE', 'none', 8),
                9: Action('SHOOT', 'n', 9),
                10: Action('SHOOT', 'ne', 10),
                11: Action('SHOOT', 'e', 11),
                12: Action('SHOOT', 'se', 12),
                13: Action('SHOOT', 's', 13),
                14: Action('SHOOT', 'sw', 14),
                15: Action('SHOOT', 'w', 15),
                16: Action('SHOOT', 'nw', 16)}

# conversion between direction string and 2d coordinate offset
dir_dict = {'n': loc(-1,0),
            'ne': loc(-1,1),
            'e': loc(0,1),
            'se': loc(1,1),
            's': loc(1,0),
            'sw': loc(1,-1),
            'w': loc(0,-1),
            'nw': loc(-1,-1),
            'none': loc(0,0)}

# conversion between observation type string and integer encoding
obs_dict = {'raw_pix': 0,
            'one_hot': 1}

class Bullet:
    """
    This class is used to describe a bullet.

    Attributes:
        loc: The current location of a bullet.
        dir: The trajectory of a bullet.
    """
    def __init__(self, _loc, _dir):
        """
        The constructor for Bullet class.
        """
        self.loc = _loc
        self.dir = _dir
    def step(self):
        """
        The function to update the location of a bullet.
        """
        self.loc =  self.loc + self.dir

class Agent():
    """
    This class is used to describe an agent.

    Attributes:
        loc: The current location of an agent.
        user: The flag indicating whether an agent is user-controlled or not.
        bullets: The dictionary to store the bullet(s) that belong to an agent.
        bullet_id: The unique id (key) of each bullet.
        bullet_cap: The number of available bullets or current capacity.
        bullet_timer: The timer keeps track of when a bullet should be reloaded.
        is_dead: The flag indicating whether an agent is dead (T) or alive (F).
    """
    def __init__(self, _loc, _user=False):
        """
        The constructor for Agent class.
        """
        self.loc = _loc
        self.user = _user
        self.bullets = {}
        self.bullet_id = 0
        self.bullet_cap = MAX_BULLETS
        self.bullet_timer = 0
        self.is_dead = False
    def step(self, map, action_index):
        """
        The function to step an agent.
        """
        # convert encoding into Action class
        action = action_dict[action_index]
        # remove bullet(s) which collide with WALL
        del_keys = []
        # iterate through bullets dictionary to find collided bullets
        for key, value in self.bullets.items():
            # update previously shot and alive bullets[key]
            self.bullets[key].step()
            index = self.bullets[key].loc
            # check collision
            if terrain_dict[map[index.r, index.c]] == 'WALL':
                del_keys.append(key)
        # delete collided bullets
        for key in del_keys:
            del self.bullets[key]
        # if an agent.is_dead == False, step current action
        if self.loc != loc(-1,-1):
            # reload if an agent satisfies the conditions
            self.reload()
            # step current action
            if action.type == 'SHOOT':
                # calculate the location of a new bullet
                bullet_loc = self.loc + dir_dict[action.dir]
                # add Bullet to bullets
                self.bullets[self.bullet_id] = Bullet(bullet_loc, dir_dict[action.dir])
                # increment id for the next Bullet
                self.bullet_id += 1
                # one bullet is decremented (used up) from capacity
                self.bullet_cap -= 1
                # if capacity is less than 0, something must have gone very wrong
                # check is_valid if the error is produced
                if self.bullet_cap < 0:
                    print('Something went wrong! Bullet count < 0.')
                    quit()
                else:
                    None
            elif action.type == 'MOVE':
                # calculate the new location of an agent
                self.loc = self.loc + dir_dict[action.dir]
            else:
                None
        else:
            None
    def reload(self):
        # check if the current capacity is less than the max capacity
        if self.bullet_cap < MAX_BULLETS:
            self.bullet_timer += 1
            if self.bullet_timer == RELOAD_SPEED:
                self.bullet_cap += 1
                self.bullet_timer = 0
            else:
                None
        # if current capacity == full capacity, don't do anything
        else:
            self.bullet_timer = 0

class Env():
    """
    The class is used to describe an environment.

    Attributes:
        height, width = The height and width of an environment.
        terrain = The one-hot encoded 3d array representing the terrain locations.
        map = The integer encoded 3d array representing the terrain locations.
        obs_type = The observation type representing the current game state.
        user = The integer representing the id controlled by the user.
        num_agents: The number of agents present in the environment.
        agents: The dictionary to store the agents that belong to an environment.
        loc_dict: The dictoonary to store the starting locations of all agents.
        action_history: The list to store the action history of all agents.
    """
    def __init__(
            self,
            _num_agents,
            _map,
            _dim,
            _loc_dict=None,
            _user=None,
            _obs_type=None):
        """
        The constructor for Env class.
        """
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
            self.loc_dict = {}
            for i in range(0, self.num_agents):
                r, c = 0, 0
                while terrain_dict[self.map[r,c]] != 'GROUND' or loc(r,c) in locs:
                    r = random.randint(0, self.height-1)
                    c = random.randint(0, self.width-1)
                locs.append(loc(r,c))
                self.loc_dict[i] = loc(r,c)
        else:
            self.loc_dict = _loc_dict
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
            self.agents[i] = Agent(self.loc_dict[i], self.user==i)
            print('Added Agent %s at %s' % (str(i), self.agents[i].loc))
        self.alive = np.arange(0, self.num_agents)
        self.action_history = []
    def step(self, action_list):
        """
        The function to update the actions of all agents indicated by action_list.

        Returns:
            observation, reward, done
        """
        self.action_history.append(action_list)
        for i in range(0, self.num_agents):
            self.agents[i].step(self.map, action_list[i])
        reward, done = self.reward()
        return self.observation(), reward, done
    def is_valid(self, index, agent):
        """
        The function to check whether an action is legal or not.

        Returns:
            valid or invalid (Bool)
        """
        a = action_dict[index]
        dest = agent.loc + dir_dict[a.dir]
        if a.type == 'MOVE':
            if terrain_dict[self.map[dest.r, dest.c]] == 'GROUND':
                return True
            else:
                return False
        elif a.type == 'SHOOT':
            if (terrain_dict[self.map[dest.r, dest.c]] == 'GROUND' \
            or terrain_dict[self.map[dest.r, dest.c]] == 'WATER') \
            and agent.bullet_cap > 0:
                return True
            else:
                return False
        else:
            print('Invalid action type.')
    def action_space(self, agent_id):
        """
        The function to return all possible valid actions of an agent.

        Returns:
            valid actions (list)
        """
        valid_actions = []
        # if agent.is_dead == True, action = move none (8)
        if self.agents[agent_id].loc == loc(-1,-1):
            valid_actions.append(8)
        else:
            for i in range(0, len(action_dict)):
                append = self.is_valid(i, self.agents[agent_id])
                if append:
                    valid_actions.append(i)
                else:
                    None
        return valid_actions
    def observation(self):
        """
        The function to return one type of observation of the environment.

        Returns:
            observation of a current state (type depends on obs_type)
        """
        # raw pixels observation
        if obs_dict[self.obs_type] == 0:
            return None
        # one-hot encoded observation
        elif obs_dict[self.obs_type] == 1:
            # initialize a numpy array
            obs = np.zeros((self.num_agents * 2 + NUM_TERRAIN-1, self.height, self.width))
            # encode agent locations
            for a_key, a in self.agents.items():
                obs[a_key, a.loc.r, a.loc.c] = 1
                # encode bullet locations
                for b_key, b in self.agents[a_key].bullets.items():
                    obs[self.num_agents + a_key, b.loc.r, b.loc.c] = 1
            # encode terrain locations
            for i in range(1, NUM_TERRAIN):
                obs[self.num_agents * 2 + (i - 1),:,:] = self.terrain[i-1,:,:]
            return obs.astype(int)
    def reward(self):
        """
        The function to return a list of rewards where each element corresponds \
        to an agent.

        Returns:
            rewards (list)
        """
        done = False
        reward = np.zeros((self.num_agents))
        print(reward.shape)
        agents = []
        bullets = []
        for key_a, a in self.agents.items():
            agents.append(a.loc.tuple())
            for key_b, b in self.agents[key_a].bullets.items():
                bullets.append(b.loc.tuple())
        common = (set(agents) & set(bullets))
        for i in range(0, len(agents)):
            # if only one agent is left standing
            if len(self.alive) == 1:
                print('Agent %s is the winner!' % (str(i)))
                print(self.action_history)
                done = True
                reward[i] = 1
                break
            # if zero agents are left standing
            elif len(self.alive) == 0:
                print('No agent wins!')
                done = True
                reward[i] = 0
                break
            # if a bullet and an agent are in the same location, that agent is dead
            elif agents[i] in common:
                self.alive = self.alive[self.alive != i]
                self.agents[i].is_dead = True
                self.agents[i].loc = loc(-1,-1)
                reward[i] = -1
            # if an agent is already dead
            elif agents[i] == (-1,-1):
                reward[i] = 0
            # if nothing else happens
            else:
                reward[i] = 0
        print(self.alive)
        return reward, done
