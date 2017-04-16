import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error


class Oracle:
    def __init__(self, gen, dataset, oracles):
        sub_oracles = [o for o in oracles if o.gen < gen]

        self.gen = gen
        self.target_index = np.random.randint(0, dataset.output.shape[1])
        self.oracles = \
            np.random.choice(sub_oracles, size=np.random.randint(0, len(sub_oracles)), replace=False) if len(sub_oracles) > 0 \
            else []
        self.model = xgb.XGBClassifier(n_estimators=20)
        self.train(dataset)

    def train(self, dataset):
        train_x = self._get_x_dataset(dataset)
        train_y = dataset.output[:, self.target_index]

        self.model.fit(train_x, train_y)

    def fitness(self, dataset):
        x = self._get_x_dataset(dataset)
        y = dataset.output[:, self.target_index]
        pred = self.model.predict(x)
        return mean_squared_error(y, pred)

    def predict_dataset(self, dataset):
        x = self._get_x_dataset(dataset)
        return self.model.predict(x)

    def predict(self, cause_input, oracle_predictions, oracle_indexes):
        x = self._get_x(cause_input, oracle_predictions, oracle_indexes)
        return self.model.predict(x)

    def enumerate_oracles(self):
        yield self
        for oracle in self.oracles:
            for sub_oracle in oracle.enumerate_oracles():
                yield sub_oracle

    def _get_x_dataset(self, dataset):
        return self._get_x(dataset.input, dataset.oracle_predictions, dataset.oracle_indexes)

    def _get_x(self, cause_input, oracle_predictions, oracle_indexes):
        if len(self.oracles) == 0:
            return cause_input

        sub_oracle_indexes = [oracle_indexes[o] for o in self.oracles]

        return np.concatenate((cause_input, oracle_predictions[:, sub_oracle_indexes]), axis=1)

    def __repr__(self):
        return "(Oracle gen {}, sub oracles {}, target {})".format(
            self.gen,
            len(self.oracles),
            self.target_index)
