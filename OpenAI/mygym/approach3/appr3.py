import gym
import numpy as np

from mygym.approach3.oracle import Oracle


def pick_action(cause, best_oracle):
    return env.action_space.sample()

def play(cause, cves, best_oracle, render=True):
    for _ in range(steps_per_epoch):
        if render:
            env.render()

        action = pick_action(cause, best_oracle)

        effect, reward, done, info = env.step(action)
        cves.append((cause, action, np.concatenate((effect, [reward, 1.0 if done else 0.0]))))
        cause = effect
        if done:
            cause = env.reset()

    return cves[-cves_max_length:], cause

def go():
    oracles = []
    cves = []
    best_oracle = None

    cause = env.reset()

    for epoch in range(epoch_count):
        cves, cause = play(cause, cves, best_oracle, render=True)

        oracles = [Oracle(0, cves, []), Oracle(0, cves, []), Oracle(0, cves, [])]

        oracle_indexes = {oracles[i]: i for i in range(len(oracles))}

        oracle_predictions = np.zeros((len(cves), len(oracles)))

        for oracle in oracles:
            pred = oracle.train(cves, None, None)

            col = oracle_indexes[oracle]
            for i in range(len(pred)):
                oracle_predictions[oracle.receptive_field.depth + i, col] = pred[i]

            print(oracle)

        oracles2 = [Oracle(1, cves, oracles), Oracle(1, cves, oracles), Oracle(1, cves, oracles)]
        for oracle in oracles2:
            oracle.train(cves, oracle_predictions, oracle_indexes)
            print(oracle)

        # dataset = Dataset(cves, oracles)
        # oracles, best_oracle = advance_oracles(dataset, oracles)
        # print('Epoch {}, oracles {}, dataset {}'.format(epoch, len(oracles), dataset))
        # for oracle in sorted(oracles, key=lambda o: o.target_index):
        #     print('Oracle {} fitness {}'.format(oracle, oracle.fitness))
        # print('')



env = gym.make('CartPole-v0')
env_actions = range(env.action_space.n)

cves_max_length = 1000
gens_count = 3
oracles_per_gen = 5
oracles_per_target = 5
epoch_count = 1
steps_per_epoch = 50

np.random.seed(123)
env.seed(456)
go()
