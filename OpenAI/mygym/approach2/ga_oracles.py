from itertools import groupby

import gym
import numpy as np
from collections import defaultdict

from mygym.approach2.dataset import Dataset
from mygym.approach2.oracle import Oracle


def pick_action(cause, best_oracle):
    if best_oracle is None or np.random.rand() > 0.1:
        return env.action_space.sample()

    cause_input = np.tile(list(cause) + [0], (len(env_actions), 1))
    cause_input[:, len(cause)] = env_actions

    oracles = list(best_oracle.enumerate_oracles())
    oracle_indexes = {oracles[i]: i for i in range(len(oracles))}

    oracle_predictions = np.ndarray((len(env_actions), len(oracles)))
    for j in range(len(oracles)):
        oracle_predictions[:, j] = oracles[j].predict(cause_input, oracle_predictions, oracle_indexes)

    return np.argmin(oracle_predictions[:, oracle_indexes[best_oracle]])


def play(frames, cause, cves, best_oracle, render=True):
    while frames > 0:
        frames -= 1
        if render:
            env.render()

        action = pick_action(cause, best_oracle)

        effect, reward, done, info = env.step(action)
        cves.append((cause, action, np.concatenate((effect, [reward, 1.0 if done else 0.0]))))
        cause = effect
        if done:
            cause = env.reset()

    return cves[-cves_max_length:], cause


def advance_oracles(dataset, oracles):
    new_oracles = list(oracles)
    for gen in range(gens_count):
        for i in range(oracles_per_gen):
            new_oracles.append(Oracle(gen, dataset, oracles))

    groups = defaultdict(list)
    for oracle in new_oracles:
        fitness = oracle.fitness(dataset)
        groups[oracle.target_index].append((oracle, fitness))

    # In effect, last two columns are (reward, done)
    done_index = dataset.effect_len - 1
    best_oracle = None

    result = set()
    for target_index, oracle_fitness in groups.items():
        sorted_by_fitness = sorted(oracle_fitness, key=lambda p: p[1])
        this_target_result = []
        for key, group in groupby(sorted_by_fitness, lambda p: p[1]):
            oracle, fitness = next(group)
            this_target_result.append(oracle)
            if len(this_target_result) > oracles_per_target:
                break

        if target_index == done_index:
            best_oracle = this_target_result[0]

        for oracle in this_target_result:
            for sub_oracle in oracle.enumerate_oracles():
                result.add(sub_oracle)

    return sorted(result, key=lambda o: o.gen), best_oracle


def test():
    oracles = []
    cves = []
    best_oracle = None

    cause = env.reset()

    for epoch in range(5):
        cves, cause = play(50, cause, cves, best_oracle, render=True)
        dataset = Dataset(cves, oracles)
        oracles, best_oracle = advance_oracles(dataset, oracles)
        print('Epoch {}, oracles {}, dataset {}'.format(epoch, len(oracles), dataset))
        for oracle in sorted(oracles, key=lambda o: o.target_index):
            print('Oracle {} fitness {}'.format(oracle, oracle.fitness(dataset)))
        print('')

env = gym.make('CartPole-v0')
env_actions = range(env.action_space.n)

cves_max_length = 1000
gens_count = 3
oracles_per_gen = 5
oracles_per_target = 5

np.random.seed(123)
env.seed(456)
test()


