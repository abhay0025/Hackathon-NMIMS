import gymnasium as gym
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import DQN

# Define your environment (replace with your actual environment)
class SimpleEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(4,), dtype=float)
        self.action_space = gym.spaces.Discrete(2)
        self.current_state = self.observation_space.sample()
        self.step_count = 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.current_state = self.observation_space.sample()
        self.step_count = 0
        info = {}  # Important: Return an info dictionary
        return self.current_state, info

    def step(self, action):
        # Simulate a simple transition
        if action == 0:
            self.current_state += 0.1
        else:
            self.current_state -= 0.1

        self.current_state = np.clip(self.current_state, 0, 1)
        self.step_count += 1
        reward = 1 if 0.4 < self.current_state < 0.6 else 0
        terminated = self.step_count >= 100
        truncated = False
        info = {}
        return self.current_state, reward, terminated, truncated, info

    def render(self):
        pass

    def close(self):
        pass

# Create an instance of your environment
env = SimpleEnv()

# It's good practice to close the environment after checking
try:
    # Check the environment for compatibility with stable-baselines3
    check_env(env)

    # If the environment is valid, you can proceed with training
    model = DQN("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)
    model.save("dqn_simple_env")

    obs, info = env.reset()
    done = False
    while not done:
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, info = env.step(action)
        env.render()
    env.close()

except Exception as e:
    print(f"Error during environment check or training: {e}")
    if hasattr(env, 'close'):
        env.close()