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
        train_x = self._get_x(dataset)
        train_y = dataset.output[:, self.target_index]

        self.model.fit(train_x, train_y)

        pred = self.model.predict(train_x)
        # print(train_y)
        # print(pred)
        print("Target index {}, fit train size {}, train err {}".format(
            self.target_index,
            len(train_x),
            mean_squared_error(train_y, pred)))

    def predict(self, dataset):
        x = self._get_x(dataset)
        return self.model.predict(x)

    def _get_x(self, dataset):
        if len(self.oracles) == 0:
            return dataset.input

        sub_oracle_indexes = [dataset.oracle_indexes[o] for o in self.oracles]

        return np.concatenate((dataset.input, dataset.oracle_predictions[:, sub_oracle_indexes]), axis=1)

    def __repr__(self):
        return "(Oracle gen {}, sub oracles {}, target {})".format(
            self.gen,
            len(self.oracles),
            self.target_index)
