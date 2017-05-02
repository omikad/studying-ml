import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error

from mygym.approach3.receptive_field import ReceptiveField


class Oracle:
    def __init__(self, epoch, cves, oracles, max_sub_oracles):
        cause, action, effect = cves[0]

        self.epoch = epoch
        self.target_index = np.random.randint(0, len(effect))

        sub_oracles = min(len(oracles), np.random.randint(0, max_sub_oracles))
        self.oracles = np.random.choice(oracles, size=sub_oracles, replace=False) \
            if len(oracles) > 0 \
            else []

        cause_len = len(cause) + 1
        depth = np.random.randint(1, 4)
        field_scheme = [(0, cause_len) for _ in range(depth)]

        self.receptive_field = ReceptiveField(field_scheme, self.oracles)
        self.model = xgb.XGBClassifier(n_estimators=10)
        self.last_fitness = 0

    def train(self, cves, oracle_predictions, oracle_indexes):
        train_boundary = int(len(cves) * 0.8)
        x = self.receptive_field.get_input(cves, oracle_predictions, oracle_indexes)
        y = np.array([e[self.target_index] for c, v, e in cves])
        self.model.fit(x[:train_boundary], y[:train_boundary])
        pred = self.model.predict(x)
        self.last_fitness = mean_squared_error(y[train_boundary:], pred[train_boundary:])
        diff = np.abs(pred - y) / (1 + np.sum(pred - y))
        return pred, diff

    def size(self):
        return self.receptive_field.input_size + len(self.oracles)

    def enumerate_oracles(self):
        yield self
        for oracle in self.oracles:
            for sub_oracle in oracle.enumerate_oracles():
                yield sub_oracle

    def __repr__(self):
        return "(Oracle epoch {}, sub oracles {}, target {}, receptive {}, fitness {})".format(
            self.epoch,
            len(self.oracles),
            self.target_index,
            self.receptive_field.input_size,
            self.last_fitness)
