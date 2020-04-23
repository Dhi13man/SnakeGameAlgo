from random import randrange, randint, choice
import os
from datetime import date, datetime

import pygame

# Colours to be used
white = (255, 255, 255)
l_white = (150, 150, 150)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
d_red = (255, 0, 0)
d_blue = (0, 0, 255)
orange = (255, 165, 0)
green = (0, 255, 0)
blue = (50, 153, 213)
colours = [white, orange, yellow, red, d_blue, d_red, green, blue]


# Set up window
class Window:
    def __init__(self):
        # Default values
        constant_w = 600
        constant_h = 480
        self.clock = pygame.time.Clock()  # time in game works now

        # Current values (might behave abnormally if changed)
        self.scrW = 600
        self.scrH = 480
        self.scale_factor = (self.scrW / constant_w + self.scrH / constant_h) / 2

        # Game window initialised
        pygame.init()
        self.win = pygame.display.set_mode((self.scrW, self.scrH))
        pygame.display.set_caption('Snek')

    # Displays message when player has lost
    def message(self, msg, color):
        font_style = pygame.font.SysFont(None, 30)
        mes = font_style.render(msg, True, color)
        self.win.blit(mes, [int(self.scrW / 2 - 230), int(self.scrH / 2)])


# Function that saves score of all snakes
def score_save():
    print("Score saved.")
    score_file = open("Scores.txt", "a")
    temp = datetime.now()

    # Write down Timestamp
    t_date = '\nDate: ' + str(temp.day) + '-' + str(temp.month) + '-' + str(temp.year)
    t_time = 'Time: ' + temp.strftime("%H:%M:%S")
    score_list = t_date + '\t' + t_time + '\n'

    # Writes down Game Parameters(Modifiable food, friendly fire on, etc)
    score_list += 'Game Parameters: '
    if friendly_fire == 1:
        score_list += 'Snake-to-Snake collision\t'
    score_list += 'Modifiable food\t' if controlled_food == 1 else ("Constant " + str(food_num) + " food ")

    # Writes down Game Speed
    score_list += '\nGame Speed: ' + str(SNEK_gtg_fast) + '\n\n'

    # Writes down Score of every Snake and Average Score
    for j, snake in enumerate(sn):
        score_list += (("AI Snake " + str(j + 1)) if not user == 1 or not j == len(sn) - 1 else "Player Snake") + ":\t" \
                      + str(snake.score) + '\n'
    average = 0
    for snake in sn:
        average += snake.score
    average = str(average / len(sn))
    score_list += '\nAverage Score = ' + average

    score_list += '\n'
    score_file.write(score_list)
    score_file.close()


# Mathematical helper functions
def dist_return(x1, y1, x2, y2):
    s = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    return s


def get_min(lis):
    m, temp = lis[0], lis
    for i in temp:
        m = i if i <= m else m
    return m


# Helper function used by game to check if snake passed edge
def beyond_edge(x, y):
    if x > window_item.scrW or x < 0 or y > window_item.scrH or y < 0:
        return True
    else:
        return False


class Snake:
    def __init__(self, x, y, col):
        self.score = 0
        self.recursion_depth = 0
        self.size = window_item.scale_factor * 10
        self.color = col
        self.x = x
        self.y = y
        self.new_x = 0
        self.new_y = 0
        self.snake_body = []
        self.snake_body_len = 1
        self.threshold = 1

    # If Snake controlled by human
    def snake_mod(self, inp):
        if inp.key == pygame.K_LEFT:
            self.new_x = -self.size
            self.new_y = 0
        elif inp.key == pygame.K_RIGHT:
            self.new_x = self.size
            self.new_y = 0
        elif inp.key == pygame.K_UP:
            self.new_x = 0
            self.new_y = -self.size
        elif inp.key == pygame.K_DOWN:
            self.new_x = 0
            self.new_y = self.size

    # If snake controlled by AI
    def snake_modAI(self, fd):
        try_list = [
            dist_return(self.x - self.size, self.y, fd.x, fd.y),  # if next movement to left
            dist_return(self.x + self.size, self.y, fd.x, fd.y),  # if next movement to right
            dist_return(self.x, self.y - self.size, fd.x, fd.y),  # if next movement upwards
            dist_return(self.x, self.y + self.size, fd.x, fd.y),  # if next movement downwards
        ]

        # Helps AI decide which part of the screen the snake's body is most localized at
        def screen_scan(current_x, current_y):
            count_x_number, count_y_number, self.threshold = 0, 0, 1 + self.snake_body_len / 500
            for part in self.snake_body:
                if current_x > part[0] + self.threshold * self.size:  # bod left
                    count_x_number += 1
                elif current_x + self.threshold * self.size < part[0]:  # bod right
                    count_x_number -= 1
                if current_y > part[1] + self.threshold * self.size:  # bod above
                    count_y_number += 1
                elif current_y + self.threshold * self.size < part[1]:  # boc below
                    count_y_number -= 1
            return [count_x_number, count_y_number]

        # Works based on where majority of snake body is located
        def based_on_body():
            scr_scan = screen_scan(self.x, self.y)
            if scr_scan[0] <= 0:
                if [(self.x - self.size), self.y] not in self.snake_body:
                    move_to_food(2)
                    return
            else:
                if scr_scan[1] >= 0:
                    move_to_food(1 if [self.x, (self.y + self.size)] not in self.snake_body else 0)
                else:
                    move_to_food(0 if [self.x, (self.y - self.size)] not in self.snake_body else 1)
                return
            if scr_scan[1] <= 0:
                if [self.x, (self.y - self.size)] not in self.snake_body:
                    move_to_food(0)
                    return
            else:
                if scr_scan[0] >= 0:
                    move_to_food(3 if [(self.x + self.size), self.y] not in self.snake_body else 2)
                else:
                    move_to_food(2 if [(self.x - self.size), self.y] not in self.snake_body else 3)
                return

        # Actual movement once AI knows that the snake is safe
        def actual_movement(flag):
            if flag == 99:
                based_on_body()
            min_distance = get_min(try_list) if flag == 99 else window_item.scrH * window_item.scrW
            if (min_distance == try_list[0] or flag == 2) and [(self.x - self.size), self.y] not in self.snake_body:
                # Snake moves left (flag 2)
                self.new_x = -self.size
                self.new_y = 0
                return 1
            elif (min_distance == try_list[1] or flag == 3) and [(self.x + self.size), self.y] not in self.snake_body:
                # Snake moves right (flag 3)
                self.new_x = self.size
                self.new_y = 0
                return 1
            elif (min_distance == try_list[2] or flag == 0) and [self.x, (self.y - self.size)] not in self.snake_body:
                # Snake moves up (flag 0)
                self.new_x = 0
                self.new_y = -self.size
                return 1
            elif (min_distance == try_list[3] or flag == 1) and [self.x, (self.y + self.size)] not in self.snake_body:
                # Snake moves down (flag 1)
                self.new_x = 0
                self.new_y = self.size
                return 1
            else:
                # Snake was not able to move
                return 0

        # Movement helper function that causes actual movement only when Snake is safe
        def move_to_food(flag):
            if not on_edge():
                moved = actual_movement(flag)
                if not moved:
                    # Try moving again with less safety standards
                    if [(self.x - self.size), self.y] not in self.snake_body and \
                            not beyond_edge(self.x - self.size, self.y):
                        # Move left
                        self.new_x = -self.size
                        self.new_y = 0
                    elif [(self.x + self.size), self.y] not in self.snake_body and \
                            not beyond_edge(self.x + self.size, self.y):
                        # Move right
                        self.new_x = self.size
                        self.new_y = 0
                    elif [self.x, (self.y - self.size)] not in self.snake_body and \
                            not beyond_edge(self.x, self.y - self.size):
                        # Move up
                        self.new_x = 0
                        self.new_y = -self.size
                    elif [self.x, (self.y + self.size)] not in self.snake_body and \
                            not beyond_edge(self.x, self.y + self.size):
                        # Move down
                        self.new_x = 0
                        self.new_y = self.size
                    else:
                        # When all else fails, run
                        self.recursion_depth += 1
                        if self.recursion_depth <= 3:
                            # Hopes movements based on majority body location will help save Snake (3 chances)
                            based_on_body()
                            return
                        elif self.recursion_depth < 6:
                            # Try to force movement by resetting AI (2 chances)
                            self.snake_modAI(fd)
                            return
                        elif self.recursion_depth < 8:
                            # Leaves direction selection to chance while avoiding own body (2 chances)
                            if [self.x, (self.y + self.size)] in self.snake_body:
                                move_to_food(choice([0, 2, 3]))
                            elif [self.x, (self.y - self.size)] in self.snake_body:
                                move_to_food(choice([1, 2, 3]))
                            elif [(self.x + self.size), self.y] in self.snake_body:
                                move_to_food(choice([0, 1, 2]))
                            elif [(self.x + self.size), self.y] in self.snake_body:
                                move_to_food(choice([0, 1, 3]))
                            return
                        elif self.recursion_depth < 9:
                            # Hopes reset of helper movement function will save snake (1 chance)
                            move_to_food(99)
                            return
                        else:
                            # AI gives up (you can add your own code here IDK)
                            pass
                else:
                    # Reset recursion depth since movement took place
                    self.recursion_depth = 0
                    return

        # Movement to save snake from edge ASAP
        def edge_moves():
            if beyond_edge(self.x - 1.8 * self.size, self.y):
                if (self.y - fd.y) >= 0:
                    actual_movement(0)
                else:
                    actual_movement(1)
            elif beyond_edge(self.x + 1.8 * self.size, self.y):
                if (self.y - fd.y) >= 0:
                    actual_movement(0)
                else:
                    actual_movement(1)
            elif beyond_edge(self.x, self.y - 1.8 * self.size):
                if (self.x - fd.x) >= 0:
                    actual_movement(3)
                else:
                    actual_movement(2)
            elif beyond_edge(self.x, self.y + 1.8 * self.size):
                if (self.x - fd.x) >= 0:
                    actual_movement(3)
                else:
                    actual_movement(2)
            return

        # AI's edge detection mechanism(detects if any edge in 180% of one Snake body piece size.)
        def on_edge():
            if ((self.x - 1.8 * self.size) < 0 or (self.x + 1.8 * self.size) > window_item.scrW or
                    (self.y - 1.8 * self.size) < 0 or (self.y + 1.8 * self.size) > window_item.scrH):
                edge_moves()
            return 0

        move_to_food(99)

    # Draws the snake based on update function
    def draw(self, size):
        last = len(self.snake_body) - 1
        for x in self.snake_body[:last]:
            pygame.draw.rect(window_item.win, self.color, [int(x[0]), int(x[1]), int(size), int(size)])
        pygame.draw.rect(window_item.win, l_white, [int(self.snake_body[last][0]), int(self.snake_body[last][1]),
                                                    int(size), int(size)])

    # Updates state of snake and finds out whether the snake has died. If not, draws snake
    def update(self):
        # Lose condition: Edge
        if beyond_edge(self.x, self.y):
            self.snake_body_len = 0
            self.snake_body.clear()

        head = []
        # Change Snake body(only if alive)
        if self.snake_body_len != 0:
            self.x += self.new_x
            self.y += self.new_y
            head = [self.x, self.y]
            self.snake_body.append(head)
            if len(self.snake_body) > self.snake_body_len:
                del self.snake_body[0]

        # Lose condition: Own body
        for x in self.snake_body[:-1]:
            if x == head:
                self.snake_body_len = 0
                self.snake_body.clear()

        # Friendly fire condition: Eats other snake and gets increased score and growth potential
        if friendly_fire == 1:
            for other_snake in sn:
                if head in other_snake.snake_body[:-1]:
                    self.snake_body_len += other_snake.snake_body_len
                    self.score += other_snake.snake_body_len
                    other_snake.snake_body_len = 0
                    other_snake.snake_body.clear()

        # Draw if hasn't lost
        if len(self.snake_body) != 0:
            self.draw(self.size)


class Food:
    def __init__(self):
        self.size = window_item.scale_factor * 10
        self.x = int(round(randrange(0, window_item.scrW - self.size) / self.size) * self.size)
        self.y = int(round(randrange(0, window_item.scrH - self.size) / self.size) * self.size)

    # Draws food
    def update(self):
        pygame.draw.rect(window_item.win, red, [int(self.x), int(self.y), int(self.size), int(self.size)])

    # Detects collision of self with assigned snake and regenerates food somewhere else accordingly
    def regen(self, snake_list):
        for this_snake in snake_list:
            # When snake reaches food and is not dead
            if this_snake.x == self.x and this_snake.y == self.y and this_snake.snake_body_len != 0:
                self.x = int(round(randrange(0, window_item.scrW - self.size) / self.size) * self.size)
                self.y = int(round(randrange(0, window_item.scrH - self.size) / self.size) * self.size)
                this_snake.snake_body_len += 1
                this_snake.score += 1
                # Assign random other food
                fs_list.__setitem__(this_snake, randrange(food_num))
                # Assign nearest food instead
                #    dist_list = []
                #    for food in fo:
                #        d = dist_return(food.x, food.y, this_snake.x, this_snake.y)
                #        dist_list.append(d)
                #    minimum = get_min(dist_list)
                #    for food_id, food in enumerate(fo):
                #        if dist_return(food.x, food.y, this_snake.x, this_snake.y) == minimum:
                #            fs_list.__setitem__(this_snake, food_id)


# Game engine
def loop():
    global food_num
    game_over = False
    game_close = False

    # Stops/Restarts Game
    def game_state_changer(this_event):
        global food_num
        if this_event.key == pygame.K_q:
            score_save()
            end, close = True, False
            return [end, close]
        elif this_event.key == pygame.K_r:
            score_save()
            end, close = False, True
            sn.clear()
            fo.clear()
            fs_list.clear()
            loop()
            return [end, close]
        elif controlled_food == 1:
            if this_event.key == pygame.K_w:
                print("Food increased!")
                food_num += 1
                fo.append(Food())
            elif this_event.key == pygame.K_s:
                print("Food decreased!")
                food_num -= 1
                fo.pop()
            for this_snake in sn:
                fs_list.__setitem__(this_snake, randrange(food_num))
            return [game_over, game_close]
        return [game_over, game_close]

    # Creates as many snake objects as needed
    for i in range(num):
        sn.append(
            Snake(window_item.scrW / 2, window_item.scrH / 2, (colours[randint(0, len(colours) - 1)]
                                                               if i >= len(colours) else colours[i])))
    # Creates as many food objects as needed
    for i in range(food_num):
        fo.append(Food())

    # Assigns food to Snakes:
    for i in range(0, num):
        if user == 0 or (user == 1 and i < num - 1):
            temp = i if i < food_num else randrange(0, food_num)
            fs_list.__setitem__(sn[i], temp)  # Different food targets given to different AIs

    # Runs till game over
    while not game_over:
        for i in range(0, num if user == 0 else num + 1):
            # Runs when snake dies
            while game_close:
                window_item.win.fill(black)
                window_item.message("A Snake died! Press R to Play Again or Q to Quit", d_red)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        game_over, game_close = game_state_changer(event)
                if game_over:
                    return
                pygame.display.update()

            # !!!!!!!!!!!!!Snakes search for food!!!!!!!!!!!!!
            if user == 0 or (user == 1 and i < num - 1):
                sn[i].snake_modAI(fo[fs_list.get(sn[i])])  # AIs search assigned food
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    game_over, game_close = game_state_changer(event)
                    if user == 1:
                        sn[num - 1].snake_mod(event)  # Human's Snake's movement
                elif event.type == pygame.QUIT:
                    game_over = True

            window_item.win.fill(black)  # Updates window

        # Updates state of Game
        for this_food in range(food_num):  # Food update
            fo[this_food].update()

        # Generate list of alive snakes
        alive_sn = []
        for snake in sn:
            if snake.snake_body_len != 0:
                alive_sn.append(snake)

        # End game if 0 alive snakes
        if len(alive_sn) == 0:
            game_close = True
        else:
            for snake in sn:  # Update alive snakes(and hence Game state too)
                snake.update()
                pygame.display.update()

            # Updates all food for all Snakes
            for i in fo:
                i.regen(sn)

            # Next time instant
            window_item.clock.tick(SNEK_gtg_fast)
    # Close windows
    pygame.quit()
    quit()


if __name__ == '__main__':
    #   Initial configurations
    num = 50  # Number of snakes
    user = 0  # Is human going to play?
    friendly_fire = 0  # Whether snakes can kill other snakes

    # Number of available food
    global food_num
    food_num = 25
    controlled_food = 0  # Whether the number of food can be changed while game is running
    # (Press 'w' to increase, 's' to decrease)

    sn = []  # List of Snakes is going to be stored here
    fo = []  # List of Food is going to be stored here
    fs_list = {}  # Which Food corresponds to which Snake

    SNEK_gtg_fast = 200  # How fast the game (vis-a-vis the Snakes) moves

    #  Game-play starts here
    window_item = Window()
    loop()
