import numpy as np


class HashableState:
    def __init__(self, board, player_idx) -> None:
        self.board = board
        self.player_idx = player_idx
        self.h = hash((board.data.tobytes(), player_idx))

    def get_valid_actions_mask(self):
        board = self.board
        return 1 - board[0, :, 0] - board[0, :, 1]

    def flip_horizontally(self):
        return HashableState(self.board[:, ::-1, :].copy(), self.player_idx)

    def __eq__(self, another):
        return self.board.shape == another.board.shape \
            and np.allclose(self.board, another.board) \
            and self.player_idx == another.player_idx

    def __hash__(self):
        return self.h


class ConnectFour:
    ROWS: int = 6
    COLS: int = 7
    state: HashableState
    done: bool
    action_mask = None

    def __init__(self):
        self.reset()

    def copy(self):
        env = ConnectFour()
        env.state = self.state
        env.done = self.done
        env.action_mask = self.action_mask.copy()
        return env

    def reset(self):
        self.state = HashableState(np.zeros((self.ROWS, self.COLS, 2), dtype=np.int32), 0)
        self.done = False
        self.action_mask = np.ones(self.COLS, dtype=np.int32)
        return self.state, self.action_mask

    def _check_win(self, board, pi):
        H = board[:, 0:4, pi] + board[:, 1:5, pi] + board[:, 2:6, pi] + board[:, 3:7, pi]
        if np.max(H) == 4:
            return True

        V = board[0:3, :, pi] + board[1:4, :, pi] + board[2:5, :, pi] + board[3:6, :, pi]
        if np.max(V) == 4:
            return True

        DD = board[0:3, 0:4, pi] + board[1:4, 1:5, pi] + board[2:5, 2:6, pi] + board[3:6, 3:7, pi]
        if np.max(DD) == 4:
            return True

        BD = board[0:3, 3:7, pi] + board[1:4, 2:6, pi] + board[2:5, 1:5, pi] + board[3:6, 0:4, pi]
        if np.max(BD) == 4:
            return True

        return False

    def step(self, action):
        board, player_idx = self.state.board, self.state.player_idx

        assert self.done == False
        assert self.action_mask[action] == 1

        ri = self.ROWS - 1
        while board[ri, action, 0] + board[ri, action, 1] > 0 and ri >= 0:
            ri -= 1
        assert ri >= 0

        board = np.copy(board)
        board[ri, action, player_idx] = 1
        if ri == 0:
            self.action_mask[action] = 0

        if self._check_win(board, player_idx):
            self.done = True
            reward = 1 - 2 * player_idx
        elif np.sum(self.action_mask) == 0:
            self.done = True
            reward = 0
        else:
            reward = 0

        self.state = HashableState(board, 1 - player_idx)
        return self.state, self.action_mask, reward, self.done

    def last(self):
        return self.state, self.action_mask

    def render_ascii(self):
        board = self.state.board
        for ri in range(board.shape[0]):
            print(''.join([
                ('0' if board[ri, ci, 0] == 1 else '1' if board[ri, ci, 1] == 1 else '.')
                for ci in range(board.shape[1])
            ]))
