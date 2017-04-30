import numpy as np


class ReceptiveField:
    def __init__(self, lines, oracles):
        self.lines = lines
        self.oracles = oracles
        self.input_size = sum(width for dx, width in lines) + len(oracles)
        self.depth = len(lines) - 1

    def get_input(self, cves, oracle_predictions, oracle_indexes):
        result = np.zeros((len(cves) - self.depth, self.input_size))

        for row in range(result.shape[0]):
            input_row = row + self.depth
            output_index = 0
            for dx, width in self.lines:
                cause, action, effect = cves[input_row]
                for j in range(width):
                    jj = dx + j

                    if jj < len(cause):
                        v = cause[jj]
                    elif jj == len(cause):
                        v = action
                    else:
                        raise StandardError('Receptive Field is out of the bounds')

                    result[row, output_index] = v
                    output_index += 1

                input_row -= 1

            for oracle in self.oracles:
                result[row, output_index] = oracle_predictions[row + self.depth, oracle_indexes[oracle]]
                output_index += 1

        return result

    def __repr__(self):
        return "(Receptive input size {}, depth {}, oracles {})".format(
            self.input_size, self.depth, len(self.oracles))