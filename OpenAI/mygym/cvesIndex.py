import Queue
from mygym.cve import Cve


class CvesIndex:
    def __init__(self, cves):
        self._cause_point_index = dict()
        if cves is not None:
            self.addlist(cves)

    def addlist(self, cves):
        for cve in cves:
            self.add(cve)

    def add(self, cve):
        if cve.cause_point not in self._cause_point_index:
            self._cause_point_index[cve.cause_point] = set()
        self._cause_point_index[cve.cause_point].add(cve)

    def __getitem__(self, cause_point):
        if cause_point in self._cause_point_index:
            return self._cause_point_index[cause_point]
        return set()

    def iteritems(self):
        return self._cause_point_index.iteritems()

    def replace(self, cause_points, replace_list):
        replace_map = dict()
        for i in xrange(len(cause_points)):
            replace_map[cause_points[i]] = replace_list[i]

        result = CvesIndex(None)
        for _, cves in self._cause_point_index.iteritems():
            for cve in cves:
                cause_idea = replace_map[cve.cause_point]
                effect_idea = replace_map[cve.effect_point] if cve.effect_point in replace_map else cve.effect_idea
                result.add(Cve(cause_idea, cve.cause_point, cve.vector, effect_idea, cve.effect_point))
        return result

    def cause_points(self):
        return self._cause_point_index.keys()

    def all_points(self):
        points = set()
        for _, cves in self._cause_point_index.iteritems():
            for cve in cves:
                points.add(cve.cause_point)
                points.add(cve.effect_point)
        return points

    def iterate_ideas_by_vector(self, start_point, width):
        queue = Queue.Queue()
        queue.put((start_point, 0))

        points = [start_point]
        ideas = [next(iter(self._cause_point_index[start_point])).cause_idea]
        used_points = set()
        used_points.add(start_point)

        while not queue.empty():
            point, dist = queue.get()
            if dist < width:
                next_points = [None] * len(Cve.Non_Game_Vectors)
                next_ideas = [None] * len(Cve.Non_Game_Vectors)

                if point in self._cause_point_index:
                    for cve in self._cause_point_index[point]:
                        next_points[cve.vector] = cve.effect_point
                        next_ideas[cve.vector] = cve.effect_idea

                    for next_point in next_points:
                        queue.put((next_point, dist + 1))

                for i in xrange(len(Cve.Non_Game_Vectors)):
                    point = next_points[i]
                    if point not in used_points:
                        used_points.add(point)
                        ideas.append(next_ideas[i])
                        points.append(point)

        return points, ideas





