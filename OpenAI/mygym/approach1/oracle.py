import numpy as np
import xgboost as xgb
from mygym.approach1.cvesIndex import CvesIndex

from mygym.approach1.cve import Cve


class Oracle:
    def __init__(self, cves, spatial_vectors_count):
        self.spatial_vectors_count = spatial_vectors_count
        self.nideas = len(Cve.Idea_Names)

        self.cves_index = CvesIndex(cves)
        print 'cves index, # of causes:', len(self.cves_index.cause_points())

        dataset = [[{'x': [], 'y': []} for _ in Cve.Vector_Names] for __ in xrange(self.nideas)]

        for cve in cves:
            if Cve.IsGameVector[cve.vector]:
                pair = dataset[cve.cause_idea][cve.vector]
                pair['x'].append(self.get_oracle_input_row(cve.cause_point, self.cves_index))
                pair['y'].append(cve.effect_idea)

        oracles = dict()
        for cause in xrange(self.nideas):
            oracles[cause] = dict()

            for vector in xrange(len(Cve.IsGameVector)):
                if Cve.IsGameVector[vector]:
                    pair = dataset[cause][vector]
                    x = np.array(pair['x'])
                    y = np.array(pair['y'])

                    if len(x) <= 4:
                        oracles[cause][vector] = None
                        continue

                    indices = np.random.permutation(len(x))
                    train_size = int(len(x) * 0.8)
                    train_idx, test_idx = indices[:train_size], indices[train_size:]
                    train_x, test_x = x[train_idx], x[test_idx]
                    train_y, test_y = y[train_idx], y[test_idx]

                    model = xgb.XGBClassifier(max_depth=3, min_child_weight=2, n_estimators=10)
                    model.fit(train_x, train_y)

                    pred = model.predict(test_x)
                    print "Fit '{}' -> {}: train/test {}/{}, err {}".format(
                        Cve.Idea_Names[cause],
                        Cve.Vector_Names[vector],
                        len(train_x),
                        len(test_x),
                        (sum(int(pred[i]) != test_y[i] for i in range(len(test_y))) / float(len(test_y))))

                    oracles[cause][vector] = model
        self.oracles = oracles

    def _print_input_data(self, cause, vector, x, y):
        for i in xrange(len(x)):
            xrow = x[i].reshape((len(x[i]) / self.nideas, self.nideas))
            s = []
            for j in xrange(len(xrow)):
                idea = '-' if sum(xrow[j]) < 0.01 else Cve.Idea_Names[np.argmax(xrow[j])]
                s.append(idea)
            print s, Cve.Idea_Names[y[i]], 'cause:vector', Cve.Idea_Names[cause], Cve.Vector_Names[vector]

    def add_cves_to_index(self, cves):
        self.cves_index.addlist(cves)

    def predict(self, point):
        x = self.get_oracle_input_row(point, self.cves_index)
        for vector in xrange(len(Cve.IsGameVector)):
            if Cve.IsGameVector[vector]:
                # idea 1 is the player
                oracle = self.oracles[1][vector]
                if oracle is not None:
                    pred = oracle.predict([x])
                    print Cve.Vector_Names[vector], '->', Cve.Idea_Names[pred[0]]

    def print_context(self, point):
        nvec = self.spatial_vectors_count
        nideas = self.nideas
        row = self.get_oracle_input_row(point, self.cves_index)
        print row.shape
        x = row.reshape((len(row) / nideas, nideas))
        vec = 0
        for ohe in x:
            print ohe, ':', Cve.Vector_Names[vec], Cve.Idea_Names[np.argmax(ohe)]
            vec = (vec + 1) % nvec

    def print_context_cves(self, point):
        for cve in self.cves_index[point]:
            print cve

    def get_oracle_input_row(self, point, cves_index):
        nvec = self.spatial_vectors_count
        nideas = self.nideas

        row = np.zeros(nvec * nideas * (1 + nvec), dtype=np.float32)

        for cve in cves_index[point]:
            if not Cve.IsGameVector[cve.vector]:
                row[(cve.vector * nideas + cve.effect_idea)] = 1

                for cve2 in cves_index[cve.effect_point]:
                    if not Cve.IsGameVector[cve2.vector]:
                        row[nvec * nideas * (1 + cve2.vector) + cve2.vector * nideas + cve2.effect_idea] = 1
        return row

