import numpy as np
from scipy import stats

# TODO: Fix
def train_discounted(env, agent, params):
    """Pass discounted reward to the agent"""
    rewards = []
    
    all_replays = []
    
    for episode in range(params.episodes_count):
        state = np.reshape(env.reset(), [1, params.state_size])        
        frame = 0
        
        states = []
        replays = []
        
        for frame in range(params.max_frame_in_episode):
            action = agent.act(state, frame)
            next_state, _, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1, params.state_size])
    
            if done:
                break

            states.append(state[0])
            replays.append((state, action, next_state))
            state = next_state
        
#         states = np.array(states)
#         predicted = agent.model.predict(states)
#         reward_value = 0.0
#         for index in reversed(range(len(replays))):
#             state, action, next_state = replays[index]
#             reward_value = reward_value * params.gamma + predicted[index, action]
#             agent.remember(state, action, reward_value, next_state)
        
        for frame, replay in enumerate(replays):
            state, action, next_state = replay
            reward_value = len(replays) - frame
            agent.remember(state, action, reward_value, next_state)
            
        rewards.append(len(replays))
            
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
    
    all_replays = []
    
    for episode in range(params.episodes_count):
        state = np.reshape(env.reset(), [1, params.state_size])        
        frame = 0
        
        states = []
        replays = []
        
        for frame in range(params.max_frame_in_episode):
            action = agent.act(state, frame)
            next_state, _, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1, params.state_size])
    
            if done:
                break

            states.append(state[0])
            replays.append((state, action, next_state))
            state = next_state
        
        for frame, replay in enumerate(replays):
            state, action, next_state = replay
            reward_value = len(replays) - frame
            agent.remember(state, action, reward_value, next_state, frame)
            
        rewards.append(len(replays))
            
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
        state = np.reshape(env.reset(), [1, params.state_size])  

        total_reward = 0.0
        
        for frame in range(params.max_frame_in_episode):
            action = agent.act(state, frame)
            next_state, reward, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1, params.state_size])
    
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

