import sys
import gym
import numpy as np
import xgboost as xgb
from gym.envs.registration import register
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
        history.append((cause, vector, effect))
    return history


def show_history_item(env, history_item):
    env.render_observation(history_item[0])
    print OsokobanEnv.Actions[history_item[1]]
    env.render_observation(history_item[2])


def show_cve_item(cve):
    print "'{}' ({}) -> {} -> '{}' ({})".format(OsokobanEnv.MapChars[cve[0]],
                                                cve[1],
                                                Vectors[cve[2]],
                                                OsokobanEnv.MapChars[cve[3]],
                                                cve[4])


def show_abstract_cve_item(acve):
    print "'{}' -> {} -> '{}'".format(OsokobanEnv.MapChars[acve[0]],
                                      Vectors[acve[1]],
                                      OsokobanEnv.MapChars[acve[2]])


def show_idea(idea):
    print "{}: '{}'".format(idea, OsokobanEnv.MapChars[idea])


def history_to_cves(env, history):
    cves = []
    deltas = [(0, -1), (-1, 0), (0, 1), (1, 0)]
    for t in xrange(len(history)):
        cause, vector, effect = history[t]
        for i in xrange(cause.shape[0]):
            for j in xrange(cause.shape[1]):
                c = cause[i, j]
                for k in xrange(4):
                    delta = deltas[k]
                    dest = (i + delta[0], j + delta[1])
                    if env.point_allowed(dest):
                        cves.append((c, (t, i, j), k, cause[dest], (t, dest[0], dest[1])))
                cves.append((c, (t, i, j), SpatialVectorsCount + vector, effect[i, j], (t + 1, i, j)))
    return cves


def get_abstract_cves(cves):
    abstract_cves = set()
    for cause, cause_point, vector, effect, effect_point in cves:
        abstract_cves.add((cause, vector, effect))
    return list(abstract_cves)


def get_ideas(abstract_cves):
    ideas = set()
    for cause, vector, effect in abstract_cves:
        ideas.add(cause)
        ideas.add(effect)
    return list(ideas)


def get_cves_index(cves):
    index = dict()
    for cve in cves:
        cause_point = cve[1]
        if cause_point not in index:
            index[cause_point] = []
        index[cause_point].append(cve)
    return index


def get_oracle_input_row(point, cves_index, nideas):
    nvec = SpatialVectorsCount
    row = np.zeros(nideas + nvec * nideas * (1 + nvec), dtype=np.float32)

    for cause, __, vector, effect, effect_point in cves_index[point]:
        row[cause] = 1

        if not IsGameVector[vector]:
            row[nideas + vector * nideas + effect] = 1

            if effect_point in cves_index:
                for ___, ____, vector2, effect2, effect_point2 in cves_index[effect_point]:
                    if not IsGameVector[vector2]:
                        row[nideas + nvec * nideas * (1 + vector) + vector2 * nideas + effect2] = 1
    return row


def get_oracles(cves, cves_index, nideas):
    dataset = [[{'x': [], 'y': []} for _ in Vectors] for __ in xrange(nideas)]

    for cause, cause_point, vector, effect, __ in cves:
        if IsGameVector[vector]:
            pair = dataset[cause][vector]
            pair['x'].append(get_oracle_input_row(cause_point, cves_index, nideas))
            pair['y'].append(effect)

    oracles = dict()
    for cause in xrange(nideas):
        oracles[cause] = dict()

        for vector in xrange(len(Vectors)):
            if IsGameVector[vector]:
                pair = dataset[cause][vector]
                x = np.array(pair['x'])
                y = np.array(pair['y'])

                if len(x) <= 4 or cause != 1:
                    oracles[cause][vector] = None
                    continue

                indices = np.random.permutation(len(x))
                train_size = int(len(x) * 0.8)
                train_idx, test_idx = indices[:train_size], indices[train_size:]
                train_x, test_x = x[train_idx], x[test_idx]
                train_y, test_y = y[train_idx], y[test_idx]

                model = xgb.XGBClassifier(max_depth=3, min_child_weight=2, n_estimators=100)
                model.fit(train_x, train_y)

                pred = model.predict(test_x)
                print "Fit '{}' -> {}: train/test {}/{}, err {}".format(
                    OsokobanEnv.MapChars[cause],
                    Vectors[vector],
                    len(train_x),
                    len(test_x),
                    (sum(int(pred[i]) != test_y[i] for i in range(len(test_y))) / float(len(test_y))))

                oracles[cause][vector] = model
    return oracles


def play():
    register(
        id='Osokoban-v0',
        entry_point='mygym.osokoban:OsokobanEnv',
        timestep_limit=1000)

    env = gym.make('Osokoban-v0')
    env.reset()

    history = get_history(env, 1000)
    show_history_item(env, history[0])

    cves = history_to_cves(env, history)
    print
    print 'cves:', len(cves)
    for cve in cves[0:10]:
        show_cve_item(cve)

    abstract_cves = get_abstract_cves(cves)
    print
    print 'abstract cves:', len(abstract_cves)
    for acve in abstract_cves[0:10]:
        show_abstract_cve_item(acve)

    ideas = get_ideas(abstract_cves)
    print
    print 'ideas:', len(ideas)
    for idea in ideas:
        show_idea(idea)

    cves_index = get_cves_index(cves)
    print 'cves index:', len(cves_index)

    nideas = len(ideas)

    oracles = get_oracles(cves, cves_index, nideas)

    env.render_observation(env.map)
    x = get_oracle_input_row((len(history) - 1, env.player_point[0], env.player_point[1]), cves_index, nideas)
    for vector in xrange(len(Vectors)):
        if IsGameVector[vector]:
            # idea 1 is the player
            oracle = oracles[1][vector]
            if oracle is not None:
                pred = oracle.predict([x])
                print Vectors[vector], '->', OsokobanEnv.MapChars[pred[0]]

play()
