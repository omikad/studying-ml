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
    rows: int
    cols: int
    wincnt: int
    state: HashableState
    done: bool

    def __init__(self, rows=6, cols=7, wincnt=4, check_ranges=None):
        self.rows = rows
        self.cols = cols
        self.wincnt = wincnt

        if check_ranges is None:
            rw1 = rows - wincnt + 1
            cw1 = cols - wincnt + 1
            check_ranges = [
                (0, rows,          0,  cw1, 0,  1),
                (0,  rw1,          0, cols, 1,  0),
                (0,  rw1,          0,  cw1, 1,  1),
                (0,  rw1, wincnt - 1, cols, 1, -1),
            ]

        self.check_ranges = check_ranges
        self.reset()

    def copy(self):
        env = ConnectFour(self.rows, self.cols, self.wincnt, self.check_ranges)
        env.state = self.state
        env.done = self.done
        env.action_mask = self.action_mask.copy()
        return env

    def reset(self):
        self.state = HashableState(np.zeros((self.rows, self.cols, 2), dtype=np.int32), 0)
        self.done = False
        self.action_mask = np.ones(self.cols, dtype=np.int32)
        return self.state, self.action_mask

    def _check_win(self, board, pi):
        wincnt = self.wincnt
        for sr, er, sc, ec, dr, dc in self.check_ranges:
            A = board[sr : er, sc : ec, pi].copy()
            for _ in range(1, wincnt):
                sr += dr
                er += dr
                sc += dc
                ec += dc
                A += board[sr : er, sc : ec, pi]
            if np.max(A) == wincnt:
                return True

        return False

    def step(self, action):
        board, player_idx = self.state.board, self.state.player_idx

        assert self.done == False
        assert self.action_mask[action] == 1

        ri = self.rows - 1
        while board[ri, action, 0] + board[ri, action, 1] > 0 and ri >= 0:
            ri -= 1
        assert ri >= 0

        board = np.copy(board)
        board[ri, action, player_idx] = 1
        if ri == 0:
            self.action_mask[action] = 0

        if self._check_win(board, player_idx):
            self.done = True
            reward = 1
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
        ConnectFour.render_board_ascii(self.state.board)

    @staticmethod
    def render_board_ascii(board):
        for ri in range(board.shape[0]):
            print(''.join([
                ('0' if board[ri, ci, 0] == 1 else '1' if board[ri, ci, 1] == 1 else '.')
                for ci in range(board.shape[1])
            ]))
