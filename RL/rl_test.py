import gymnasium as gym  # ✅ Use gymnasium instead of gym
from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from RL import TrafficEnv

env = TrafficEnv()
check_env(env)  # ✅ Should work now

model = DQN("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)

model.save("dqn_traffic_model")
print("✅ Training complete. Model saved.")
