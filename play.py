from helper import *
from env import *
from policy import *

NUM_AGENTS = 2
ENV = 'env_0'
loc_dict = {0: loc(1,1), 1: loc(5,5)}
DIM = (7,7)

# setup
e = Env(NUM_AGENTS, ENV, DIM, _loc_dict=loc_dict, _obs_type='one_hot')

policies = {}
for i in range(0, e.num_agents):
    policies[i] = policy(_e0=1)

for n in range(0, 10):
    action_list = []
    for i in range(0, e.num_agents):
        action_space = e.action_space(i)
        action_list.append(policies[i].action(action_space))
    e.step(action_list)
    print(e.observation())
print(e.reward())
