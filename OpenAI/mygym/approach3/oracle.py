import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error

from mygym.approach3.receptive_field import ReceptiveField


class Oracle:
    def __init__(self, gen, cves, oracles):
        sub_oracles = [o for o in oracles if o.gen < gen]

        cause, action, effect = cves[0]

        self.gen = gen
        self.target_index = np.random.randint(0, len(effect))
        self.oracles = \
            np.random.choice(sub_oracles, size=np.random.randint(0, len(sub_oracles)), replace=False) \
            if len(sub_oracles) > 0 \
            else []
        self.receptive_field = ReceptiveField([(0, len(cause) + 1)], self.oracles)
        self.model = xgb.XGBClassifier(n_estimators=10)

    def train(self, cves, oracle_predictions, oracle_indexes):
        x = self.receptive_field.get_input(cves, oracle_predictions, oracle_indexes)
        y = [e[self.target_index] for c,v,e in cves[self.receptive_field.depth:]]
        self.model.fit(x, y)
        pred = self.model.predict(x)
        self.last_fitness = mean_squared_error(y, pred)
        return pred

    def __repr__(self):
        return "(Oracle gen {}, sub oracles {}, target {}, receptive {}, fitness {})".format(
            self.gen,
            len(self.oracles),
            self.target_index,
            self.receptive_field.input_size,
            self.last_fitness)
