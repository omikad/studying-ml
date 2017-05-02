import numpy as np
import xgboost as xgb

class ActionPicker:
    def __init__(self, env_actions, cves, diff, best_oracle):
        self.best_oracle = best_oracle

        cause_len = len(cves[0][0])

        x = np.zeros((len(cves), cause_len + 1))

        for row in range(x.shape[0]):
            cause, vector, effect = cves[row]

            for i in range(cause_len):
                x[row, i] = cause[i]

            x[row, cause_len] = vector

        model = xgb.XGBClassifier(n_estimators=50)
        model.fit(x, diff)

        cause, vector, effect = cves[-1]
        acts = np.zeros((len(env_actions), x.shape[1]))

        for act_index in range(len(env_actions)):
            for i in range(cause_len):
                acts[act_index, i] = effect[i]

            acts[act_index, cause_len] = env_actions[act_index]

        y = model.predict(acts)

        max_error = np.argmax(y)

        self.recommended_action = env_actions[max_error]

        print(y, max_error, self.recommended_action)
