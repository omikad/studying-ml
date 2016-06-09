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

    @property
    def cause_points(self):
        return self._cause_point_index.keys()





