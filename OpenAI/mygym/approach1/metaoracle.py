import numpy as np
from mygym.approach1.cvesIndex import CvesIndex
from mygym.approach1.hashableArray import HashableArray

from mygym.approach1.cve import Cve


class MetaOracle:
    def __init__(self, oracle):
        self.idea_chars = {idx: ch for idx, ch in enumerate(Cve.Idea_Names)}
        self.idea_chars[None] = '?'
        self.oracle = oracle
        self.cves_index = oracle.cves_index
        self.learn_meta_oracle()

    def learn_meta_oracle(self):
        x = []
        y = []

        for world, world_start_point in self.generate_random_worlds(5, 2):
            world_points, world_ideas = world.iterate_ideas_by_vector(world_start_point, 2)

            effects = set()
            effects.add(HashableArray(world_ideas))

            self._process_world(world, world_points, world_ideas, effects, 3)

            for effect in effects:
                effect_ideas = effect.unwrap()

                self.render_world(world)
                print world_ideas
                print effect_ideas

                nideas = len(Cve.Idea_Names)
                nhalf = len(world_ideas) * nideas
                row = np.zeros(2 * nhalf)
                for i in xrange(len(world_ideas)):
                    before = world_ideas[i]
                    after = effect_ideas[i]
                    if before != after:
                        row[i * nideas + before] = 1
                        row[nhalf + i * nideas + after] = 1

                print row
                print len(row)

                return

        # diff = [None] * 2 * len(world_ideas)
        # for i in xrange(len(world_ideas)):
        #     before = world_ideas[i]
        #     after = replace_list[i]
        #     diff[i] = before if before != after else None
        #     diff[i + len(world_ideas)] = after if before != after else None
        # print diff

    def _process_world(self, world, world_points, world_ideas, effects, depth):
        if depth > 0:
            for vector in Cve.Game_Vectors:
                effect_ideas = self.predict(world, world_points, world_ideas, vector)
                effect_world = world.replace(world_points, effect_ideas)

                if HashableArray(effect_ideas) not in effects:
                    effects.add(HashableArray(effect_ideas))
                    self._process_world(effect_world, world_points, effect_ideas, effects, depth - 1)

    def predict(self, world, world_points, world_ideas, vector):
        replace_list = []
        for i in xrange(len(world_points)):
            idea = world_ideas[i]
            if idea >= 0:
                point = world_points[i]
                row = self.oracle.get_oracle_input_row(point, world)
                prediction = self.oracle.oracles[idea][vector].predict([row])[0]
                replace_list.append(prediction)
            else:
                replace_list.append(idea)
        return np.array(replace_list, dtype=np.int32)

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

            random_worlds.append((world, point))

        return random_worlds





