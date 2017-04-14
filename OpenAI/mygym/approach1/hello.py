import sys

import gym
import numpy as np
from gym.envs.registration import register
from mygym.approach1.cve import Cve
from mygym.approach1.oracle import Oracle
from mygym.approach1.osokoban import OsokobanEnv

from mygym.approach1.metaoracle import MetaOracle

SpatialVectorsCount = 4
Deltas = [(0, -1), (-1, 0), (0, 1), (1, 0)]


def get_action_from_user():
    while True:
        key = sys.stdin.read(1)
        if key == 'a':
            return OsokobanEnv.Left
        if key == 'w':
            return OsokobanEnv.Up
        if key == 'd':
            return OsokobanEnv.Right
        if key == 's':
            return OsokobanEnv.Down
        if key == ' ':
            return OsokobanEnv.Restart


def get_history(env, count):
    history = []
    for _ in xrange(count):
        cause = env.map.copy()
        vector = env.action_space.sample()
        effect, reward, done, info = env.step(vector)
        history.append((cause, vector + SpatialVectorsCount, effect.copy()))
    return history


def play_with_user_oracle(env, history, oracle):
    t = len(history) + 1
    while True:
        env.render_observation(env.map)

        cves = []
        add_spatial_cves(env, cves, env.map, t)
        oracle.add_cves_to_index(cves)

        last_player_point = (t, env.player_point[0], env.player_point[1])
        oracle.predict(last_player_point)

        vector = get_action_from_user()
        env.step(vector)
        t += 1


def show_history_item(env, history_item):
    env.render_observation(history_item[0])
    print Cve.Vector_Names[history_item[1]]
    env.render_observation(history_item[2])


def show_abstract_cve_item(acve):
    print "'{}' -> {} -> '{}'".format(Cve.Idea_Names[acve[0]],
                                      Cve.Vector_Names[acve[1]],
                                      Cve.Idea_Names[acve[2]])


def show_idea(idea):
    print "{}: '{}'".format(idea, Cve.Idea_Names[idea])


def add_spatial_cves(env, cves, level, t):
    for i in xrange(level.shape[0]):
        for j in xrange(level.shape[1]):
            c = level[i, j]
            for k in xrange(4):
                delta = Deltas[k]
                dest = (i + delta[0], j + delta[1])
                if env.point_allowed(dest):
                    cves.append(Cve(c, (t, i, j), k, level[dest], (t, dest[0], dest[1])))


def history_to_cves(env, history):
    cves = []
    for t in xrange(len(history)):
        cause, vector, effect = history[t]
        add_spatial_cves(env, cves, cause, t)
        for i in xrange(cause.shape[0]):
            for j in xrange(cause.shape[1]):
                c = cause[i, j]
                cves.append(Cve(c, (t, i, j), vector, effect[i, j], (t + 1, i, j)))
    add_spatial_cves(env, cves, history[-1][2], len(history))
    return cves


def get_abstract_cves(cves):
    abstract_cves = set()
    for cve in cves:
        abstract_cves.add((cve.cause_idea, cve.vector, cve.effect_idea))
    return list(abstract_cves)


def play():
    np.random.seed(1351)    # 1348, 1351

    register(
        id='Osokoban-v0',
        entry_point='mygym.osokoban:OsokobanEnv',
        timestep_limit=1000)

    env = gym.make('Osokoban-v0')
    # env.shape = (4, 4)
    # env.walls_lim = (0, 1)
    # env.diamonds_lim = (0, 1)
    env.reset()

    history = get_history(env, 500)
    cves = history_to_cves(env, history)
    abstract_cves = get_abstract_cves(cves)

    print 'cves:', len(cves)
    print 'abstract cves:', len(abstract_cves)
    print 'ideas:', len(OsokobanEnv.MapChars)

    oracle = Oracle(cves, SpatialVectorsCount)
    print

    # play_with_user_oracle(env, history, oracle)

    metaoracle = MetaOracle(oracle)

play()




