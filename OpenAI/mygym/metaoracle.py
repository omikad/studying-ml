import numpy as np


class MetaOracle:
    def __init__(self, idea_chars, oracle, is_game_vector):
        self.idea_chars = {idx: ch for idx, ch in enumerate(idea_chars)}
        self.idea_chars[None] = '?'
        self.oracle = oracle
        self.is_game_vector = is_game_vector
        self.cves_index = oracle.cves_index
        random_worlds = self.generate_random_worlds(10, 2)
        self.render_world(random_worlds[0])

    def render_world(self, cves_index):
        points = set()
        for cause_point, cves in cves_index.iteritems():
            for cve in cves:
                points.add(cve[1])
                points.add(cve[4])
        minr = min((p[1] for p in points))
        minc = min((p[2] for p in points))
        maxr = max((p[1] for p in points))
        maxc = max((p[2] for p in points))
        arr = [[None]*(maxc - minc + 1) for _ in range(maxr - minr + 1)]
        for cause_point, cves in cves_index.iteritems():
            for cve in cves:
                point0 = cve[1]
                point1 = cve[4]
                arr[point0[1] - minr][point0[2] - minc] = cve[0]
                arr[point1[1] - minr][point1[2] - minc] = cve[3]

        out = [[self.idea_chars[i] for i in line] for line in arr]
        print '\n'.join([''.join(row) for row in out])

    def generate_random_worlds(self, count, width):
        random_worlds = []

        cves_keys = self.cves_index.keys()
        points = [cves_keys[i] for i in (np.random.permutation(len(self.cves_index))[:count])]

        for point in points:
            world = dict()
            stack = [point]
            lengths = [0]
            while len(stack) > 0:
                cur_point = stack.pop()
                cur_len = lengths.pop()

                if cur_len <= width and cur_point in self.cves_index:
                    cves = self.cves_index[cur_point]
                    for cve in cves:
                        if not self.is_game_vector[cve[2]]:
                            if cur_point not in world:
                                world[cur_point] = set()
                            world[cur_point].add(cve)
                            stack.append(cve[4])
                            lengths.append(cur_len + 1)

            random_worlds.append(world)

        return random_worlds





