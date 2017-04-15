import gym
import numpy as np

from mygym.approach2.dataset import Dataset
from mygym.approach2.oracle import Oracle


def play(frames, cves):
    while frames > 0:
        cause = env.reset()
        while frames > 0:
            frames -= 1
            env.render()
            action = env.action_space.sample()
            effect, reward, done, info = env.step(action)
            cves.append((cause, action, np.concatenate((effect, [reward, 1.0 if done else 0.0]))))
            cause = effect
            if done:
                break

    if len(cves) > 5000:
        cves = cves[len(cves) - 5000:]

    return cves


def test():
    cves = play(30, [])
    dataset = Dataset(cves, [])
    print(dataset)

    oracles2 = [Oracle(0, dataset, []), Oracle(0, dataset, []), Oracle(0, dataset, [])]
    dataset2 = Dataset(cves, oracles2)
    print(dataset2)

    oracles3 = oracles2 + [Oracle(1, dataset2, oracles2), Oracle(1, dataset2, oracles2)]
    dataset3 = Dataset(cves, oracles3)
    print(dataset3)

env = gym.make('CartPole-v0')
np.random.seed(123)
env.seed(456)
test()


