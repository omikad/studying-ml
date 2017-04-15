from itertools import groupby

import gym
import numpy as np
from collections import defaultdict

from mygym.approach2.dataset import Dataset
from mygym.approach2.oracle import Oracle


def play(frames, cves, render=True):
    while frames > 0:
        cause = env.reset()
        while frames > 0:
            frames -= 1
            if render: env.render()
            action = env.action_space.sample()
            effect, reward, done, info = env.step(action)
            cves.append((cause, action, np.concatenate((effect, [reward, 1.0 if done else 0.0]))))
            cause = effect
            if done:
                break

    return cves[-1000:]


def advance_oracles(dataset, oracles):
    new_oracles = list(oracles)
    for gen in range(3):
        for i in range(5):
            new_oracles.append(Oracle(gen, dataset, oracles))

    groups = defaultdict(list)
    for oracle in new_oracles:
        fitness = oracle.fitness(dataset)
        groups[oracle.target_index].append((oracle, fitness))

    result = set()
    for target_index, oracle_fitness in groups.items():
        sorted_by_fitness = sorted(oracle_fitness, key=lambda p: p[1])
        this_target_result = []
        for key, group in groupby(sorted_by_fitness, lambda p: p[1]):
            oracle, fitness = next(group)
            this_target_result.append(oracle)
            if len(this_target_result) > 5:
                break

        for oracle in this_target_result:
            for sub_oracle in oracle.enumerate_oracles():
                result.add(sub_oracle)

    return sorted(result, key=lambda o: o.gen)


def test():
    oracles = []
    cves = []

    for epoch in range(11):
        cves = play(50, cves, render=False)
        dataset = Dataset(cves, oracles)
        oracles = advance_oracles(dataset, oracles)
        print('Epoch {}, oracles {}, dataset {}'.format(epoch, len(oracles), dataset))
        for oracle in sorted(oracles, key=lambda o: o.target_index):
            print('Oracle {} fitness {}'.format(oracle, oracle.fitness(dataset)))
        print('')

env = gym.make('CartPole-v0')
env_actions = range(env.action_space.n)

np.random.seed(123)
env.seed(456)
test()


