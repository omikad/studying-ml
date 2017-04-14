import gym

env = gym.make('CartPole-v0')

for i_episode in range(1):
    observation = env.reset()
    print(observation)
    for t in range(5):
        env.render()
        actions = env.action_space
        print('Actions', actions)
        action = actions.sample()
        observation, reward, done, info = env.step(action)
        print('Reward', reward)
        print(observation)
        if done:
            print("Episode finished after {} steps".format(t + 1))
            break
