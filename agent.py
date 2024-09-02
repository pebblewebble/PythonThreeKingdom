import torch
import random
import numpy as np
from collections import deque
from gameAI import SnakeGame, Point
from model import Linear_QNet, QTrainer
from helper import plot
import pygame

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 80 - self.n_games  # randomness
        self.gamma = 0.99  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        # 11 is the number of states, 3 is the number of actions we can do
        self.model = Linear_QNet(10, 256, 4)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        point = game.player[0]

        nearest_food = self.find_nearest(point, game.food)
        nearest_enemy = self.find_nearest(point, game.reds + game.blues + game.greens)

        state = [
            # Normalized position of the player's point
            point.x / game.w,
            point.y / game.h,
            # Normalized direction to nearest food
            (nearest_food.x - point.x) / game.w if nearest_food else 0,
            (nearest_food.y - point.y) / game.h if nearest_food else 0,
            # Normalized direction to nearest enemy (regardless of color)
            (nearest_enemy.x - point.x) / game.w if nearest_enemy else 0,
            (nearest_enemy.y - point.y) / game.h if nearest_enemy else 0,
            # Danger in four directions (binary values)
            self.is_direction_dangerous(game, point, "left"),
            self.is_direction_dangerous(game, point, "right"),
            self.is_direction_dangerous(game, point, "up"),
            self.is_direction_dangerous(game, point, "down"),
        ]

        return np.array(state, dtype=float)

    def find_nearest(self, point, objects):
        if not objects:
            return None
        nearest = min(objects, key=lambda obj: self.distance(point, obj))
        return nearest

    def distance(self, point1, point2):
        return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5

    def is_direction_dangerous(self, game, point, direction):
        x, y = point.x, point.y
        size = point.width/2
        if direction == "left":
            x -= size
        elif direction == "right":
            x += size
        elif direction == "up":
            y -= size
        elif direction == "down":
            y += size

        # Check if the new position would collide with any enemy
        for enemy in game.reds + game.blues + game.greens:
            if pygame.Rect(x, y, point.width, point.height).colliderect(enemy):
                return 1

        # Check if the new position is out of bounds
        # if x < 0 or x >= game.w or y < 0 or y >= game.h:
            # return 1

        return 0

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) < BATCH_SIZE:
            mini_sample = random.sample(
                self.memory, BATCH_SIZE
            )  # returns a list of tuple
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            # Might need to change later
            move = int(torch.argmax(prediction).item())
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGame()
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)
        reward, done, score = game.play_step(final_move)

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()
            print("Game", agent.n_games, "Score", score, "Record:", record)

            # Plot
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

        state_new = agent.get_state(game)

        # train shrot memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)
      

if __name__ == "__main__":
    train()
