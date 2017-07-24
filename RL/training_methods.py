import numpy as np
from scipy import stats

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
            # !!! reset the sum, since this was a game boundary (pong specific!)
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
            agent.think(32)
        
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
            agent.think(32)
        
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
            agent.think(32)
        
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