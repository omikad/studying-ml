import numpy as np


class Dataset:
    # Must sure oracles sorted by gen
    def __init__(self, cves, oracles):
        if len(cves) == 0:
            raise RuntimeError("Can't create dataset")

        first_cause, first_vector, first_effect = cves[0]

        self.cause_len = len(first_cause)
        self.action_index = len(first_cause)

        self.input = np.ndarray((len(cves), len(first_cause) + 1))
        self.oracle_predictions = np.ndarray((len(cves), len(oracles)))
        self.output = np.ndarray((len(cves), len(first_effect)))

        for i in range(len(cves)):
            cause, vector, effect = cves[i]

            for j in range(self.cause_len):
                self.input[i, j] = cause[j]

            self.input[i, self.action_index] = vector

            for j in range(len(effect)):
                self.output[i, j] = effect[j]

        self.oracle_indexes = {oracles[i]: i for i in range(len(oracles))}
        for j in range(len(oracles)):
            self.oracle_predictions[:, j] = oracles[j].predict(self)

    def __repr__(self):
        return "(Dataset input {}, oracle predictions {}, output {})".format(
            self.input.shape,
            self.oracle_predictions.shape,
            self.output.shape)
