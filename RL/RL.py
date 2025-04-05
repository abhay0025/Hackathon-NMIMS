import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random

class TrafficEnv(gym.Env):
    def __init__(self):
        super(TrafficEnv, self).__init__()

        # Action: 0 = North-South Green, 1 = East-West Green
        self.action_space = spaces.Discrete(2)

        self.observation_space = spaces.Box(low=0, high=20, shape=(4,), dtype=np.int32)

        self.max_steps = 100
        self.currrent_step = 0

        self.reset()

    def reset(self, seed=None, options = None):
        super().reset(seed=seed)
        self.state = np.random.randint(0, 20, size=(4,))  # random initial topic
        self.currrent_step = 0
        return self.state
    
    def step(self, action):
        north, south, east, west = self.state
        
        if action == 0:  # NS green
            cars_passed = min(north, 5), min(south, 5)
            north -= cars_passed[0]
            south -= cars_passed[1]
            east += random.randint(0, 3)
            west += random.randint(0, 3)
        else:  # EW green
            cars_passed = min(east, 5), min(west, 5)
            east -= cars_passed[0]
            west -= cars_passed[1]
            north += random.randint(0, 3)
            south += random.randint(0, 3)

        self.state = np.array([north, south, east, west])

        # Reward: negative of total waiting cars
        reward = -np.sum(self.state)

        self.currrent_step += 1
        done = self.currrent_step >= self.max_steps
        
        info = {"cars_waiting_total": np.sum(self.state)}

        return self.state, reward, done, False, info

    def render(self):
        print(f"Step {self.current_step} - Traffic (N,S,E,W): {self.state}")


