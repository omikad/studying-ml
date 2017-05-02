# coding=utf-8
from itertools import groupby

import gym
import numpy as np
from collections import defaultdict

from mygym.approach3.action_picker import ActionPicker
from mygym.approach3.oracle import Oracle


def pick_action(cause, action_picker):
    return env.action_space.sample()


def train_oracles(epoch, cves, old_oracles):
    oracles = list(old_oracles)

    for i in range(oracles_per_epoch):
        oracles.append(Oracle(epoch, cves, old_oracles, max_sub_oracles))

    total_diff = np.zeros((len(cves)))
    oracle_indexes = {oracles[i]: i for i in range(len(oracles))}
    oracle_predictions = np.zeros((len(cves), len(oracles)))
    for oracle in oracles:
        pred, diff = oracle.train(cves, oracle_predictions, oracle_indexes)
        total_diff = total_diff + diff

        col = oracle_indexes[oracle]
        for i in range(len(pred)):
            oracle_predictions[i, col] = pred[i]

    groups = defaultdict(list)
    for oracle in oracles:
        groups[oracle.target_index].append(oracle)

    # In effect, last two columns are (reward, done)
    done_index = len(cves[0][2]) - 1
    best_oracle = None

    result = set()
    for target_index, oracles_same_target in groups.items():
        this_target_result = []
        for key, oracles_same_fitness in groupby(oracles_same_target, lambda o: o.last_fitness):
            oracle = sorted(oracles_same_fitness, key=lambda o: o.size())[0]
            this_target_result.append(oracle)
            if len(this_target_result) > oracles_per_target:
                break

        if target_index == done_index:
            best_oracle = this_target_result[0]

        for oracle in this_target_result:
            for sub_oracle in oracle.enumerate_oracles():
                result.add(sub_oracle)

    action_picker = ActionPicker(env_actions, cves, total_diff, best_oracle)

    return sorted(result, key=lambda o: o.epoch), action_picker


def play(cause, cves, action_picker, render=True):
    for _ in range(steps_per_epoch):
        if render:
            env.render()

        action = pick_action(cause, action_picker)

        effect, reward, done, info = env.step(action)
        cves.append((cause, action, np.concatenate((effect, [reward, 1.0 if done else 0.0]))))
        cause = effect
        if done:
            cause = env.reset()

    return cves[-cves_max_length:], cause


def go():
    oracles = []
    cves = []
    action_picker = None

    cause = env.reset()

    for epoch in range(epoch_count):
        cves, cause = play(cause, cves, action_picker, render=True)

        oracles, action_picker = train_oracles(epoch, cves, oracles)

        print('Epoch {}, oracles {}, cves {}'.format(epoch, len(oracles), len(cves)))
        for oracle in sorted(oracles, key=lambda o: o.target_index):
            print(oracle)
        print('')


env = gym.make('CartPole-v0')
env_actions = range(env.action_space.n)

cves_max_length = 1000
oracles_per_epoch = 5
oracles_per_target = 5
max_sub_oracles = 5
epoch_count = 5
steps_per_epoch = 100

np.random.seed(123)
env.seed(456)
go()
