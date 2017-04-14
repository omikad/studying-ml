import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error


class Oracle:
    def __init__(self, gen, cves, oracles):
        if len(cves) == 0:
            raise RuntimeError("Can't create oracle without data")

        first_effect = cves[0][1]
        sub_oracles = [o for o in oracles if o.gen < gen]

        self.gen = gen
        self.target_index = np.random.randint(0, len(first_effect))
        self.oracles = np.random.choice(sub_oracles, replace=False) if len(sub_oracles) > 0 else []
        self.model = xgb.XGBClassifier(n_estimators=20)
        self.train(cves)

    def train(self, cves):
        train_x = np.array([x for x, y in cves])
        train_y = np.array([y[self.target_index] for x, y in cves])

        self.model.fit(train_x, train_y)

        pred = self.model.predict(train_x)
        # print(train_y)
        # print(pred)
        print("Target index {}, fit train size {}, train err {}".format(
            self.target_index,
            len(train_x),
            mean_squared_error(train_y, pred)))

    def predict(self, cve):
        return self.model.predict(cve[0])