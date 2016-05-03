import sys
import gym
from gym.envs.registration import register

from mygym.oracle import Oracle
from mygym.osokoban import OsokobanEnv

Vectors = ["Left", "Up", "Right", "Down", "KeyLeft", "KeyUp", "KeyRight", "KeyDown", "KeyRestart"]
IsGameVector = [False, False, False, False, True, True, True, True, True]
SpatialVectorsCount = 4
GameVectorsCount = 5


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


def show_history_item(env, history_item):
    env.render_observation(history_item[0])
    print Vectors[history_item[1]]
    env.render_observation(history_item[2])


def show_abstract_cve_item(acve):
    print "'{}' -> {} -> '{}'".format(OsokobanEnv.MapChars[acve[0]],
                                      Vectors[acve[1]],
                                      OsokobanEnv.MapChars[acve[2]])


def show_idea(idea):
    print "{}: '{}'".format(idea, OsokobanEnv.MapChars[idea])


def add_spatial_cves(env, deltas, cves, level, t):
    for i in xrange(level.shape[0]):
        for j in xrange(level.shape[1]):
            c = level[i, j]
            for k in xrange(4):
                delta = deltas[k]
                dest = (i + delta[0], j + delta[1])
                if env.point_allowed(dest):
                    cves.append((c, (t, i, j), k, level[dest], (t, dest[0], dest[1])))


def history_to_cves(env, history):
    cves = []
    deltas = [(0, -1), (-1, 0), (0, 1), (1, 0)]
    for t in xrange(len(history)):
        cause, vector, effect = history[t]
        add_spatial_cves(env, deltas, cves, cause, t)
        for i in xrange(cause.shape[0]):
            for j in xrange(cause.shape[1]):
                c = cause[i, j]
                cves.append((c, (t, i, j), vector, effect[i, j], (t + 1, i, j)))
    add_spatial_cves(env, deltas, cves, history[-1][2], len(history))
    return cves


def get_abstract_cves(cves):
    abstract_cves = set()
    for cause, cause_point, vector, effect, effect_point in cves:
        abstract_cves.add((cause, vector, effect))
    return list(abstract_cves)


def play():
    register(
        id='Osokoban-v0',
        entry_point='mygym.osokoban:OsokobanEnv',
        timestep_limit=1000)

    env = gym.make('Osokoban-v0')
    # env.shape = (4, 4)
    # env.walls_lim = (0, 1)
    env.diamonds_lim = (0, 1)
    env.reset()

    history = get_history(env, 1000)
    cves = history_to_cves(env, history)
    abstract_cves = get_abstract_cves(cves)

    print 'cves:', len(cves)
    print 'abstract cves:', len(abstract_cves)
    print 'ideas:', len(OsokobanEnv.MapChars)

    oracle = Oracle(cves, SpatialVectorsCount, IsGameVector, Vectors, OsokobanEnv.MapChars)

    env.render_observation(env.map)
    last_player_point = (len(history), env.player_point[0], env.player_point[1])

    oracle.predict(last_player_point)

play()
