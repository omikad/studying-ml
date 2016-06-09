import numpy as np

from mygym.cve import Cve
from mygym.cvesIndex import CvesIndex


class MetaOracle:
    def __init__(self, oracle):
        self.idea_chars = {idx: ch for idx, ch in enumerate(Cve.Idea_Names)}
        self.idea_chars[None] = '?'
        self.oracle = oracle
        self.cves_index = oracle.cves_index
        random_worlds = self.generate_random_worlds(10, 2)
        self.render_world(random_worlds[0])
        self.predict(random_worlds[0], Cve.Game_Vectors[0])

    def predict(self, world, vector):
        print Cve.Vector_Names[vector], ':'
        for cause_point, cves in world.iteritems():
            row = self.oracle.get_oracle_input_row(cause_point, world)
            cause_idea = next(iter(cves)).cause_idea
            prediction = self.oracle.oracles[cause_idea][vector].predict([row])[0]
            print cause_point, Cve.Idea_Names[cause_idea], Cve.Idea_Names[prediction]

    def render_world(self, cves_index):
        points = set()
        for _, cves in cves_index.iteritems():
            for cve in cves:
                points.add(cve.cause_point)
                points.add(cve.effect_point)
        minr = min((p[1] for p in points))
        minc = min((p[2] for p in points))
        maxr = max((p[1] for p in points))
        maxc = max((p[2] for p in points))
        arr = [[None]*(maxc - minc + 1) for _ in range(maxr - minr + 1)]
        for _, cves in cves_index.iteritems():
            for cve in cves:
                point0 = cve.cause_point
                point1 = cve.effect_point
                arr[point0[1] - minr][point0[2] - minc] = cve.cause_idea
                arr[point1[1] - minr][point1[2] - minc] = cve.effect_idea

        out = [[self.idea_chars[i] for i in line] for line in arr]
        print '\n'.join([''.join(row) for row in out])

    def generate_random_worlds(self, count, width):
        random_worlds = []

        cves_keys = self.cves_index.cause_points
        points = [cves_keys[i] for i in (np.random.permutation(len(cves_keys))[:count])]

        for point in points:
            world = CvesIndex(None)
            stack = [point]
            lengths = [0]
            while len(stack) > 0:
                cur_point = stack.pop()
                cur_len = lengths.pop()

                if cur_len <= width:
                    cves = self.cves_index[cur_point]
                    for cve in cves:
                        if not Cve.IsGameVector[cve.vector]:
                            world.add(cve)
                            stack.append(cve.effect_point)
                            lengths.append(cur_len + 1)

            random_worlds.append(world)

        return random_worlds





