import sys
import numpy as np
import gym
from gym import spaces, utils
from six import StringIO


class OsokobanEnv(gym.Env):
    """
    Classic Sokoban game

    Reward is equal to the count of correctly placed diamonds

    Rendered map ASCII characters:
        Space: empty cell
        &: Player
        #: Wall
        O: Diamond
        .: Empty chest
        +: Chest with diamond
    """

    metadata = {'render.modes': ['human', 'ansi']}

    # Game items
    Empty, Player, Wall, Diamond, Chest, FullChest = range(6)
    MapChars = [' ', '&', '#', 'O', '.', '+']

    # Game actions
    Left, Up, Right, Down, Restart = range(5)
    Actions = ["Left", "Up", "Right", "Down", "Restart"]
    _deltas = [(0, -1), (-1, 0), (0, 1), (1, 0)]

    def __init__(self, shape=(6, 4), walls_lim=(2, 10), diamonds_lim=(1, 5)):
        self.shape = shape
        self.walls_lim = walls_lim
        self.diamonds_lim = diamonds_lim
        n_actions = 5
        n_cell_types = 5
        self.lastaction = None
        self.action_space = spaces.Discrete(n_actions)
        self.observation_space = spaces.Discrete(self.shape[0] * self.shape[1] * n_cell_types)
        self._new_level()

    def _reset(self):
        self._new_level()
        return self.map

    def _step(self, action):
        self.lastaction = action

        if action == self.Restart:
            self._new_level()
            return self.map, 0, False, None

        self._move_player(self._deltas[action])

        reward = np.sum(self.map == self.FullChest)

        return self.map, reward, reward >= self.diamonds and reward > 0, None

    def _move_player(self, delta):
        dest = self._sum_points(self.player_point, delta)

        if not self.point_allowed(dest):
            return

        destitem = self.map[dest]

        if destitem == self.Empty or destitem == self.Chest:
            self.map[self.player_point] = self.behind_player
            self.behind_player = destitem
            self.player_point = dest
            self.map[dest] = self.Player
            return

        if destitem == self.Diamond or destitem == self.FullChest:
            nextdest = self._sum_points(dest, delta)
            if not self.point_allowed(nextdest):
                return

            nextdestitem = self.map[nextdest]

            if nextdestitem == self.Empty:
                self.map[nextdest] = self.Diamond
            elif nextdestitem == self.Chest:
                self.map[nextdest] = self.FullChest
            else:
                return

            self.map[self.player_point] = self.behind_player

            if destitem == self.Diamond:
                self.behind_player = self.Empty
            else:
                self.behind_player = self.Chest

            self.player_point = dest
            self.map[dest] = self.Player

    def _render(self, mode='human', close=False):
        if close:
            return

        outfile = StringIO() if mode == 'ansi' else sys.stdout

        if self.lastaction is not None:
            outfile.write("  ({})\n".format(self.Actions[self.lastaction]))

        self.render_observation(self.map, outfile)
        outfile.write("\n")

        if mode != 'human':
            return outfile

    def render_observation(self, observation, outfile=sys.stdout):
        out = observation.copy().tolist()
        out = [[self.MapChars[i] for i in line] for line in out]

        b = utils.colorize(' ', 'gray', highlight=True)
        bline = "{}{}{}\n".format(b, b * observation.shape[1], b)
        outfile.write(bline)
        outfile.write("\n".join([(b + "".join(row) + b) for row in out]) + "\n")
        outfile.write(bline)

    def _new_level(self):
        walls = np.random.randint(self.walls_lim[0], self.walls_lim[1])
        self.diamonds = np.random.randint(self.diamonds_lim[0], self.diamonds_lim[1])
        self.map = np.zeros(self.shape, dtype=int)
        self._fill_map_item(walls, self.Wall)
        self._fill_map_item(self.diamonds, self.Diamond)
        self._fill_map_item(self.diamonds, self.Chest)
        self.player_point = self._fill_map_item(1, self.Player)
        self.behind_player = self.Empty

    def _fill_map_item(self, count, item):
        point = (0, 0)
        while count > 0:
            point = (np.random.randint(self.shape[0]), np.random.randint(self.shape[1]))
            if self.map[point] == 0:
                self.map[point] = item
                count -= 1
        return point

    @staticmethod
    def _sum_points(x, y):
        return x[0] + y[0], x[1] + y[1]

    def point_allowed(self, point):
        return 0 <= point[0] < self.shape[0] and 0 <= point[1] < self.shape[1]

