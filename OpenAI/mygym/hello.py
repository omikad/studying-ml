import sys
import gym
from gym.envs.registration import register
from mygym.osokoban import OsokobanEnv

register(
    id='Osokoban-v0',
    entry_point='mygym.osokoban:OsokobanEnv',
    timestep_limit=1000,
)


def get_action_from_user():
    while True:
        key = sys.stdin.read(1)
        if key == 'a':
            return OsokobanEnv.Left
        if key == 'w':
            return OsokobanEnv.Up
        if key == 'd':
            return OsokobanEnv.Right
        if key == 's':
            return OsokobanEnv.Down
        if key == ' ':
            return OsokobanEnv.Restart

env = gym.make('Osokoban-v0')
env.reset()

print type(OsokobanEnv)

for _ in xrange(100):
    env.render()

    action = get_action_from_user()

    observation, reward, done, info = env.step(action)

    if done:
        break

    print reward



