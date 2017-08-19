# jupyter notebook &
# tensorboard --logdir="logs" &

# TODO: pass global step to optimizer

import numpy as np
import math
from scipy import stats

class LearningParameters:
    def __init__(self, env, episodes_count):
        state = env_reset(env)

        self.state_shape = state.shape
        self.state_size = np.prod(self.state_shape)
        self.action_size = env.action_space.n
        self.episodes_count = episodes_count
        self.max_frame_in_episode = env.spec.max_episode_steps
        self.max_memory_size = 10000
        self.episodes_between_think = 1
        
        self.gamma = 0.95                # discount rate
        self.epsilon = 1.0               # exploration rate
        self.epsilon_start = self.epsilon
        self.epsilon_min = 0.0001        # min exploration rate
        self.learning_rate = 0.1         # learning rate for algorithm
        self.learning_rate_model = 0.01  # learning rate for model
        
        print("State shape {}, actions {}".format(self.state_shape, self.action_size))

    def decay_exploration_rate(self, episode):
        # Linear exploration rate decay (lerp)
#         self.epsilon = self.epsilon_start - \
#                       (self.epsilon_start - self.epsilon_min) * (float(frame) / self.frames_count)
            
        # Exponential rate decay
        # y(0) = start
        # y(1) = start * x
        # y(2) = start * x^2
        # y(steps) = start * x^steps = min => x = (min/start) ^ (1/steps)
        # y(t) = start * x^t
        self.epsilon = self.epsilon_start * \
                       math.pow( math.pow(self.epsilon_min / self.epsilon_start, 1.0 / self.episodes_count), episode )

def show(env, agent, params, frames, width, height, greedy=True):
    state = env_reset(env)
    img = plt.imshow(state.reshape(width, height))
    frame = 0
    for _ in range(frames):
        img.set_data(state.reshape(width, height))
        display.display(plt.gcf())
        display.clear_output(wait=True)

        action = agent.act_greedy(state, frame) if greedy else np.random.randint(0, params.action_size)
        state, reward, done, _ = env_step(env, action)
        if done:
            state = env_reset(env)
            frame = 0
        else:
            frame += 1

def train_discounted_rewards(env, agent, params, normalize_rewards):
    rewards = []
    
    for episode in range(params.episodes_count):
        state = env_reset(env)
        total_reward = 0.0
        
        replays = []
        
        for frame in range(params.max_frame_in_episode):
            action = agent.act(state, frame)
            next_state, reward, done, _ = env_step(env, action)

            total_reward += reward
    
            if done:
                break

            replays.append((frame, state, action, reward, next_state))
            state = next_state

        rewards.append(total_reward)

        episode_rewards = np.zeros(len(replays))
        discounted_reward = 0.0
        for i in reversed(range(len(replays))):
            reward = replays[i][3]
            # !!!!!!!! reset the sum, since this was a game boundary (pong specific!)
            # if reward != 0: discounted_reward = 0
            discounted_reward = reward + discounted_reward * params.gamma
            episode_rewards[i] = discounted_reward

        if normalize_rewards:
            episode_rewards -= np.mean(episode_rewards)
            std = np.std(episode_rewards)
            if std != 0:
            	episode_rewards /= std

        for i in range(len(replays)):
            frame, state, action, _, next_state = replays[i]
            agent.remember(state, action, episode_rewards[i], next_state, frame)

        if (episode + 1) % max(1, (params.episodes_count / 20)) == 0:
            print("episode: {}/{}, reward {}, frames {}, exploration rate: {:.2}"
                .format(episode + 1, params.episodes_count, np.mean(rewards[-10:]), len(replays), params.epsilon))
            
        if (episode + 1) % params.episodes_between_think == 0:
            agent.think(32, episode)
        
        params.decay_exploration_rate(episode)

    return agent, rewards

def train_reward_is_time(env, agent, params):
    """Ignore reward from the env, agent will be trained to increase total time played"""
    rewards = []
    
    for episode in range(params.episodes_count):
        state = env_reset(env)
        
        replays = []
        
        for frame in range(params.max_frame_in_episode):
            action = agent.act(state, frame)
            next_state, _, done, _ = env_step(env, action)

            if done:
                break

            replays.append((state, action, next_state))
            state = next_state
            
        rewards.append(len(replays))
        
        for frame, replay in enumerate(replays):
            state, action, next_state = replay
            reward_value = len(replays) - frame
            agent.remember(state, action, reward_value, next_state, frame)
            
        if (episode + 1) % max(1, (params.episodes_count / 20)) == 0:
            print("episode: {}/{}, reward {}, frames {}, exploration rate: {:.2}"
                .format(episode + 1, params.episodes_count, np.mean(rewards[-10:]), len(replays), params.epsilon))
            
        if (episode + 1) % params.episodes_between_think == 0:
            agent.think(32, episode)
        
        params.decay_exploration_rate(episode)

    return agent, rewards

def train(env, agent, params):   
    rewards = []
    
    for episode in range(params.episodes_count):
        state = env_reset(env)
        total_reward = 0.0
        
        for frame in range(params.max_frame_in_episode):
            action = agent.act(state, frame)
            next_state, reward, done, _ = env_step(env, action)
    
            total_reward += reward
    
            if done:
                reward = -10
    
            if frame < env.spec.max_episode_steps:
                agent.remember(state, action, reward, next_state, frame)
                
            state = next_state
            
            if done:
                break
        
        rewards.append(total_reward)
            
        if (episode + 1) % max(1, (params.episodes_count / 20)) == 0:
            print("episode: {}/{}, reward {}, exploration rate: {:.2}"
                .format(episode + 1, params.episodes_count, np.mean(rewards[-10:]), params.epsilon))
            
        if (episode + 1) % params.episodes_between_think == 0:
            agent.think(32, episode)
        
        params.decay_exploration_rate(episode)

    return agent, rewards

def evaluate(env, agent, params, frames):
    state = env_reset(env)
    total_reward = 0
    for e in range(frames):
        action = agent.act_greedy(state, e)
        state, reward, done, _ = env_step(env, action)
        total_reward += reward
        if done or e == frames - 1:
            break
    print("Total reward: {}".format(total_reward))

def env_reset(env):
    return env.my_preprocess_input(env.reset())

def env_step(env, action):
    n, r, d, i = env.step(action)
    return env.my_preprocess_input(n), r, d, i

def preprocess_input_pong_v0(I):
    I = I[35:195]
    I[I == 144] = 0
    I[I == 109] = 0
    I = I[::2,::2,0] + I[1::2,::2,0] + I[::2,1::2,0] + I[1::2,1::2,0]
    I = I[::2,::2] + I[1::2,::2] + I[::2,1::2] + I[1::2,1::2]
    I = I[::2,::2] + I[1::2,::2] + I[::2,1::2] + I[1::2,1::2]
    I[I != 0] = 1
    I = I[0:19, 2:18]
    return I.astype(np.float).ravel()

def preprocess_input_breakout_v0(I):
    I = I[35:195, 10:150]  # crop to (160, 140, 3)
    I = (I[:,:,0] + I[:,:,1] + I[:,:,2]) / 3
    I = I[::2,::2] + I[1::2,::2] + I[::2,1::2] + I[1::2,1::2]
    return I.astype(np.float).ravel()