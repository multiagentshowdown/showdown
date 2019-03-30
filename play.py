from helper import *
from env import *
from policy import *
from render import *

NUM_AGENTS = 4
ENV = 'env_0'
loc_dict = {0: loc(1,1), 1: loc(5,5), 2: loc(5,1), 3: loc(1,5)}
DIM = (7,7)
SCALE = 25

# setup env
e = Env(NUM_AGENTS, ENV, DIM, _loc_dict=loc_dict, _obs_type='one_hot')
# initialize pygame
window = window(SCALE, (e.height,e.width))

policies = {}
for i in range(0, e.num_agents):
    policies[i] = policy(_e0=1)

for n in range(0, 10000):
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            quit()
    window.render(e, 0.5)
    # rgb = pygame.surfarray.array3d(screen)
    action_list = []
    for i in range(0, e.num_agents):
        action_space = e.action_space(i)
        opt_action = policies[i].action(action_space)
        action_list.append(opt_action)
        print(action_dict[opt_action])
    observation, reward, done = e.step(action_list)
    for i in range(0, e.num_agents):
        print('Agent %s: %s' % (str(i), str(e.agents[i].bullet_cap)))
    if done:
        print(reward)
        quit()
