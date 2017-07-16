import numpy as np
from scipy import stats

def train_discounted_rewards(env, agent, params):
    rewards = []
    
    for episode in range(params.episodes_count):
        state = env.reset()
        total_reward = 0.0
        
        replays = []
        
        for frame in range(params.max_frame_in_episode):
            action = agent.act(state, frame)
            next_state, reward, done, _ = env.step(action)

            total_reward += reward
    
            if done:
                break

            replays.append((frame, state, action, reward, next_state))
            state = next_state

        rewards.append(total_reward)

        discounted_reward = 0.0
        for frame, state, action, reward, next_state in reversed(replays):
            discounted_reward = reward + discounted_reward * params.gamma
            agent.remember(state, action, discounted_reward, next_state, frame)

        if (episode + 1) % max(1, (params.episodes_count / 20)) == 0:
            print("episode: {}/{}, reward {}, exploration rate: {:.2}"
              .format(episode + 1, params.episodes_count, np.mean(rewards[-10:]), params.epsilon))
            
        if (episode + 1) % params.episodes_between_think == 0:
            agent.think(32)
        
        params.decay_exploration_rate(episode)

    return agent, rewards

def train_reward_is_time(env, agent, params):
    """Ignore reward from the env, agent will be trained to increase total time played"""
    rewards = []
    
    for episode in range(params.episodes_count):
        state = env.reset()
        
        replays = []
        
        for frame in range(params.max_frame_in_episode):
            action = agent.act(state, frame)
            next_state, _, done, _ = env.step(action)

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
            print("episode: {}/{}, reward {}, exploration rate: {:.2}"
              .format(episode + 1, params.episodes_count, np.mean(rewards[-10:]), params.epsilon))
            
        if (episode + 1) % params.episodes_between_think == 0:
            agent.think(32)
        
        params.decay_exploration_rate(episode)

    return agent, rewards

def train(env, agent, params):   
    rewards = []
    
    for episode in range(params.episodes_count):
        state = env.reset()
        total_reward = 0.0
        
        for frame in range(params.max_frame_in_episode):
            action = agent.act(state, frame)
            next_state, reward, done, _ = env.step(action)
    
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

