import math
import unittest
import random

import numpy as np

from src.agents.sac import SAC
from src.envs.probe_envs import ConstRewardEnv, PredictableRewardEnv, TwoActionsTwoStates
from src.utils.utils import evaluate_policy
import torch


class TestSAC(unittest.TestCase):

    def test_value_function_const_env(self):
        places = 3
        env = ConstRewardEnv()
        sac = SAC(env, entropy_scale=0.2, lr=0.01, buffer_size=1, batch_size=1, hidden_size=256, num_layers=2)
        sac.train(num_steps=1000)
        self.assertAlmostEqual(1, sac.get_value(([0], 0)).item(), places=places)

    def test_value_function_predicable_env(self):
        places = 3
        env = PredictableRewardEnv()
        sac = SAC(env, entropy_scale=0.2, lr=0.01, buffer_size=1, batch_size=1, hidden_size=256, num_layers=2)
        sac.train(num_steps=2000)
        self.assertAlmostEqual(1, sac.value([1, 0]).item(), places=places)
        self.assertAlmostEqual(-1, sac.value([-1, 0]).item(), places=places)

    def test_policy_two_action_two_states(self):
        delta = 0.2

        # Check if optimal policy can be adopted
        env = TwoActionsTwoStates()
        sac = SAC(env, entropy_scale=0.2, discount_factor=1, lr=0.01, buffer_size=100, batch_size=20,
                  hidden_size=256, num_layers=2)
        sac.train(num_steps=4000)

        avg = evaluate_policy(sac.policy.act, env, trials=1000, rtmdp_ob=False)
        self.assertAlmostEqual(2, avg, delta=delta)
        self.assertAlmostEqual(2, sac.value([0, 0]).item(), delta=delta)
        self.assertAlmostEqual(2, sac.value([1, 0]).item(), delta=delta)
        self.assertAlmostEqual(1, sac.value([2, 1]).item(), delta=delta)
        self.assertAlmostEqual(1, sac.value([3, 0]).item(), delta=delta)

    def test_entropy(self):
        # Check if random policy is adopted when entropy is valued extremely highly
        env = TwoActionsTwoStates()
        sac = SAC(env, entropy_scale=10, discount_factor=1, lr=0.03, buffer_size=200, batch_size=16,
                  hidden_size=256, num_layers=2)
        sac.train(num_steps=4000)
        avg = evaluate_policy(sac.policy.act, env, trials=1000, rtmdp_ob=False)

        self.assertAlmostEqual(1.5, avg, delta=0.3)
        self.assertAlmostEqual(2 * 10 * math.log(2, math.e), sac.value([0, 1]).item(), delta=10)
        self.assertAlmostEqual(1 * 10 * math.log(2, math.e), sac.value([3, 1]).item(), delta=10)

    def test_get_value(self):
        env = TwoActionsTwoStates()
        initial_state = env.reset()
        sac = SAC(env, entropy_scale=10, discount_factor=1, lr=0.03, buffer_size=200, batch_size=16,
                  hidden_size=256, num_layers=2)
        value = sac.get_value((initial_state, 0))
        dist = sac.get_action_distribution(initial_state)

        self.assertTrue(isinstance(value, torch.Tensor))
        self.assertTrue(isinstance(dist, torch.Tensor))

    def test_target_network(self):
        delta = 0.1

        # Check if optimal policy can be adopted
        env = TwoActionsTwoStates()
        sac = SAC(env, entropy_scale=0.2, discount_factor=1, lr=0.01, buffer_size=100, batch_size=20,
                  hidden_size=256, num_layers=2, use_target=True)
        sac.train(num_steps=4000)

        avg = evaluate_policy(sac.policy.act, env, trials=1000, rtmdp_ob=False)
        self.assertAlmostEqual(2, avg, delta=delta)
        self.assertAlmostEqual(2, sac.value([0, 0]).item(), delta=delta)
        self.assertAlmostEqual(2, sac.value([1, 0]).item(), delta=delta)
        self.assertAlmostEqual(1, sac.value([2, 1]).item(), delta=delta)
        self.assertAlmostEqual(1, sac.value([3, 0]).item(), delta=delta)

    def test_double_network(self):
        delta = 0.1

        # Check if optimal policy can be adopted
        env = TwoActionsTwoStates()
        sac = SAC(env, entropy_scale=0.2, discount_factor=1, lr=0.01, buffer_size=100, batch_size=20,
                  hidden_size=256, num_layers=2, double_value=True)
        sac.train(num_steps=4000)

        avg = evaluate_policy(sac.policy.act, env, trials=1000, rtmdp_ob=False)
        self.assertAlmostEqual(2, avg, delta=delta)
        self.assertAlmostEqual(2, sac.value([0, 0]).item(), delta=delta)
        self.assertAlmostEqual(2, sac.value([1, 0]).item(), delta=delta)
        self.assertAlmostEqual(1, sac.value([2, 1]).item(), delta=delta)
        self.assertAlmostEqual(1, sac.value([3, 0]).item(), delta=delta)