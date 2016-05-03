import numpy as np
import xgboost as xgb


class Oracle:
    def __init__(self, cves, spatial_vectors_count, is_game_vector, vector_names, idea_names):
        self.spatial_vectors_count = spatial_vectors_count
        self.nideas = len(idea_names)
        self.is_game_vector = is_game_vector
        self.vector_names = vector_names
        self.idea_names = idea_names

        self.cves_index = self._get_cves_index(cves)
        print 'cves index:', len(self.cves_index)

        dataset = [[{'x': [], 'y': []} for _ in is_game_vector] for __ in xrange(self.nideas)]

        for cause, cause_point, vector, effect, ___ in cves:
            if is_game_vector[vector]:
                pair = dataset[cause][vector]
                pair['x'].append(self._get_oracle_input_row(cause_point))
                pair['y'].append(effect)

        oracles = dict()
        for cause in xrange(self.nideas):
            oracles[cause] = dict()

            for vector in xrange(len(is_game_vector)):
                if is_game_vector[vector]:
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

                    print 'train', train_x.shape, 'test', test_x.shape

                    pred = model.predict(test_x)
                    print "Fit '{}' -> {}: train/test {}/{}, err {}".format(
                        idea_names[cause],
                        vector_names[vector],
                        len(train_x),
                        len(test_x),
                        (sum(int(pred[i]) != test_y[i] for i in range(len(test_y))) / float(len(test_y))))

                    oracles[cause][vector] = model
        self.oracles = oracles

    def predict(self, point):
        x = self._get_oracle_input_row(point)
        for vector in xrange(len(self.is_game_vector)):
            if self.is_game_vector[vector]:
                # idea 1 is the player
                oracle = self.oracles[1][vector]
                if oracle is not None:
                    pred = oracle.predict([x])
                    print self.vector_names[vector], '->', self.idea_names[pred[0]]

    def print_context(self, point):
        nvec = self.spatial_vectors_count
        nideas = self.nideas
        row = self._get_oracle_input_row(point)
        print row.shape
        x = row.reshape((len(row) / nideas, nideas))
        vec = 0
        for ohe in x:
            print ohe, ':', self.vector_names[vec], self.idea_names[np.argmax(ohe)]
            vec = (vec + 1) % nvec

    def _get_oracle_input_row(self, point):
        nvec = self.spatial_vectors_count
        nideas = self.nideas
        cves_index = self.cves_index

        row = np.zeros(nvec * nideas * (1 + nvec), dtype=np.float32)

        for cause, _, vector, effect, effect_point in cves_index[point]:
            if not self.is_game_vector[vector]:
                row[vector * nideas + effect] = 1

                if effect_point in cves_index:
                    for ___, ____, vector2, effect2, _____ in cves_index[effect_point]:
                        if not self.is_game_vector[vector2]:
                            row[nvec * nideas * (1 + vector) + vector2 * nideas + effect2] = 1
        return row

    @staticmethod
    def _get_cves_index(cves):
        index = dict()
        for cve in cves:
            cause_point = cve[1]
            if cause_point not in index:
                index[cause_point] = []
            index[cause_point].append(cve)
        return index
