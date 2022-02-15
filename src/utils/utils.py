import random
from collections import deque
from typing import Union, Any, Tuple, List

import numpy as np
import torch
from torch import Tensor


class ReplayBuffer:

    def __init__(self, capacity: int):
        self.buffer = deque(maxlen=capacity)

    def __len__(self):
        return len(self.buffer)

    def add_data(self, data: Tuple[Any, float, Any, bool]):  # state, reward, next_state, done
        self.buffer.append(data)

    def capacity_reached(self):
        return len(self.buffer) >= self.buffer.maxlen

    def sample(self, sample_size: int) -> List[Tuple[Any, float, Any, bool]]:
        return random.sample(self.buffer, sample_size)


@torch.no_grad()
def moving_average(target_params, current_params, factor):
    for t, c in zip(target_params, current_params):
        t += factor * (c - t)


def flatten_rtmdp_obs(obs: Union[np.ndarray, Tensor], num_actions: int) -> list[Any]:
    """
    Converts the observation tuple (s,a) returned by rtmdp
    into a single sequence s + one_hot_encoding(a)
    """
    # one-hot action encoding
    one_hot = np.zeros(num_actions)
    one_hot[obs[1]] = 1
    return list(obs[0]) + list(one_hot)


def evaluate_policy(policy, env, trials=10, rtmdp_ob=True) -> float:
    cum_rew = 0
    for _ in range(trials):
        state = env.reset()
        done = False
        while not done:
            if rtmdp_ob:
                state = flatten_rtmdp_obs(state, env.action_space.n)
            action = policy(state)
            state, reward, done, _ = env.step(action)
            cum_rew += reward

    return cum_rew / trials
