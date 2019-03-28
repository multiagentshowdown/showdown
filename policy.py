import math
import random
import numpy as np

class policy:
    def __init__(
            self,
            _e0=.1,
            _l=0):
        self.e0 = _e0
        self.e = _e0
        self.l = _l
        self.t = 0
        # TODO: add cnn later
        self.cnn = None
    def action(self, valid_actions):
        self.t += 1
        self.e = self.e0 * math.exp(-1 * self.l * self.t)
        if random.random() < self.e:
            return random.choice(valid_actions)
        else:
            Q_values = None
            for i in range(0, len(Q_values)):
                if i in valid_actions:
                    continue
                else:
                    Q_values[i] = np.NINF
            return np.argmax(Q_values)
