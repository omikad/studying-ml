import numpy as np

from mygym.cve import Cve
from mygym.cvesIndex import CvesIndex


class MetaOracle:
    def __init__(self, oracle):
        self.idea_chars = {idx: ch for idx, ch in enumerate(Cve.Idea_Names)}
        self.idea_chars[None] = '?'
        self.oracle = oracle
        self.cves_index = oracle.cves_index
        self.learn_meta_oracle()

    def learn_meta_oracle(self):
        random_worlds = self.generate_random_worlds(10, 2)
        for world in random_worlds:
            world_cause_points = world.cause_points()
            original_list = world.get_ideas(world_cause_points)
            for vector in Cve.Game_Vectors:
                replace_list = self.predict(world, world_cause_points, vector)
                self.render_world(random_worlds[0])
                print Cve.Vector_Names[vector], ':'
                self.render_world(world.replace(world_cause_points, replace_list))
                print original_list
                print replace_list
                print sum(original_list[i] != replace_list[i] for i in xrange(len(original_list)))
                return

    def predict(self, world, world_cause_points, vector):
        replace_list = []
        for cause_point in world_cause_points:
            row = self.oracle.get_oracle_input_row(cause_point, world)
            cause_idea = next(iter(world[cause_point])).cause_idea
            prediction = self.oracle.oracles[cause_idea][vector].predict([row])[0]
            replace_list.append(prediction)
        return replace_list

    def render_world(self, cves_index):
        points = cves_index.all_points()
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

        cves_keys = self.cves_index.cause_points()
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





