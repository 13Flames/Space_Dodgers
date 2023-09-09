import pygame
import time
import random
import logging

pygame.font.init()
pygame.display.init()
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
PLAYER_VEL = 7
STAR_VEL = 3
paused = False
PAUSE_COOLDOWN = 500
last_pause_time = 0
WIN = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], 0, 0, 0)
pygame.display.set_caption("Space Dodgers")

BG = pygame.transform.scale(pygame.image.load("Black_BG.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
PLAYER_IMAGE = pygame.image.load("SpaceShip.png").convert_alpha()
PLAYER_STAND = pygame.transform.rotozoom(pygame.image.load("SpaceShip.png"), 0, 2)
PLAYER_STAND_RECT = PLAYER_STAND.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

PLAYER_WIDTH = 35
PLAYER_HEIGHT = 40
STAR_WIDTH = 10
STAR_HEIGHT = 20

STAR_IMAGE = pygame.transform.scale(pygame.image.load("Star.png"), (STAR_WIDTH, STAR_HEIGHT))

FONT = pygame.font.SysFont("comic sans", 30)

DIFFICULTIES = {
    'Easy': {'star_vel': 2, 'star_spawn_rate': 2500, 'player_vel': 8, 'star_vel_increment': 0},
    'Medium': {'star_vel': 3, 'star_spawn_rate': 2000, 'player_vel': 7, 'star_vel_increment': 0.3},
    'Hard': {'star_vel': 5, 'star_spawn_rate': 1000, 'player_vel': 6, 'star_vel_increment': 0.7},
    'Expert': {'star_vel': 7, 'star_spawn_rate': 800, 'player_vel': 5, 'star_vel_increment': 1.7},
}


class Star:
    def __init__(self, velocity):
        self.x = random.randint(0, SCREEN_WIDTH - STAR_WIDTH)
        self.y = -STAR_HEIGHT
        self.velocity = velocity

    def move(self):
        self.y += self.velocity

    def fall(self):
        self.y += STAR_VEL

    def draw(self, win):
        win.blit(STAR_IMAGE, (self.x, self.y))

    def collision(self, obj):
        return collide(self, obj)


def collide(obj1, obj2):
    obj1_rect = pygame.Rect(obj1.x, obj1.y, STAR_WIDTH, STAR_HEIGHT)
    obj2_rect = pygame.Rect(obj2.x, obj2.y, PLAYER_WIDTH, PLAYER_HEIGHT)
    return obj1_rect.colliderect(obj2_rect)


def handle_movement(keys, player):
    if keys[pygame.K_LEFT] and player.x - PLAYER_VEL > 0:  # Left movement
        player.x -= PLAYER_VEL
    if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width < SCREEN_WIDTH:  # Right movement
        player.x += PLAYER_VEL


def load_scores():
    scores = []
    try:
        with open("leaderboard.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                name, score, difficulty = line.strip().split(',')
                scores.append((name, int(score.strip()), difficulty.strip()))
        return scores
    except FileNotFoundError:
        return []


def filter_highscores():
    all_scores = []
    best_scores = {}  # dictionary to keep track of highest score per player for each difficulty

    try:
        with open("leaderboard.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                name, score, difficulty = line.strip().split(',')
                score = int(score.strip())
                key = (name, difficulty.strip())  # Combine name and difficulty for the key

                # If this key doesn't exist in best_scores or the score is higher than the existing one
                if key not in best_scores or score > best_scores[key]:
                    best_scores[key] = score

                all_scores.append((name, score, difficulty.strip()))

        # Create a new list that contains only the best scores per player for each difficulty
        highscores = [(name, score, difficulty) for name, score, difficulty in all_scores if
                      best_scores[(name, difficulty)] == score]

        return highscores
    except FileNotFoundError:
        logging.error("File not found.")
        return []
    except Exception as e:
        logging.error(f"Error filtering scores: {e}")
        return []


def save_scores(scores):
    scores.sort(key=lambda x: x[1], reverse=True)
    with open("leaderboard.txt", "w") as file:
        for name, score, difficulty in scores:
            file.write(f"{name.strip()}, {score}, {difficulty.strip()}\n")


def update_leaderboard(name, score, difficulty):
    try:
        scores = load_scores()
        if not isinstance(scores, list):
            print("Error: Scores data is not a list.")
            scores = []
        scores.append((name, score, difficulty))
        scores.sort(key=lambda x: x[1], reverse=True)
        save_scores(scores)
    except Exception as e:
        print(f"Error updating leaderboard: {e}")


def display_leaderboard(difficulty):
    WIN.blit(BG, (0, 0))
    title = FONT.render("Leaderboard", 1, (255, 255, 255))
    WIN.blit(title, (SCREEN_WIDTH / 2 - title.get_width() / 2, 50))
    scores = filter_highscores()
    if difficulty:
        scores = [s for s in scores if s[2] == difficulty]

    for i, (name, score, _) in enumerate(scores[:10], 1):
        score_text = FONT.render(f"{i}. {name}: {score}", 1, (255, 255, 255))
        WIN.blit(score_text, (SCREEN_WIDTH / 2 - score_text.get_width() / 2, 100 + 40 * i))

    pygame.display.update()


def get_player_name():
    enter_name = FONT.render("Enter Name", 1, (255, 255, 255))
    input_box = pygame.Rect(SCREEN_WIDTH / 2 - 70, SCREEN_HEIGHT / 2, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue3')
    color = color_inactive
    active = False
    text = ''
    font = pygame.font.Font(None, 32)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return text
            if event.type == pygame.KEYDOWN:
                active = not active
            else:
                active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        WIN.blit(BG, (0, 0))
        WIN.blit(txt_surface, (input_box.x+5, input_box.y+5))
        WIN.blit(enter_name, (input_box.x+20, input_box.y+30))
        pygame.draw.rect(WIN, color, input_box, 2)

        pygame.display.flip()
        pygame.time.Clock().tick(30)


def draw(player, stars, score):
    WIN.blit(BG, (0, 0))

    score_text = FONT.render(f"Score: {round(score)}", 1, (255, 255, 255))
    WIN.blit(score_text, (10, 10))

    WIN.blit(PLAYER_IMAGE, player)

    for star in stars:
        star.draw(WIN)

    pygame.display.update()


def main_menu():
    run = True

    while run:
        WIN.blit(BG, (0, 0))
        # FONT
        title_font = pygame.font.SysFont("comic sans", 70)
        leaderboard_font = pygame.font.SysFont("comic sans", 50)
        quit_font = pygame.font.SysFont("comic sans", 50)
        # TEXT
        easy_label = FONT.render("Easy", 1, (255, 255, 255))
        medium_label = FONT.render("Medium", 1, (255, 255, 255))
        hard_label = FONT.render("Hard", 1, (255, 255, 255))
        expert_label = FONT.render("Expert", 1, (255, 255, 255))
        title_label = title_font.render("Space Dodgers", 1, (255, 255, 255))
        leaderboard_label = leaderboard_font.render("View Leaderboard", 1, (255, 255, 255))
        quit_label = quit_font.render("Quit", 1, (255, 255, 255))
        bw, bh = 150, 70
        # DRAW ON SCREEN
        difficulty_labels = [("Easy", SCREEN_WIDTH / 4),
                             ("Medium", SCREEN_WIDTH / 2),
                             ("Hard", 3 * SCREEN_WIDTH / 4)]
        for difficulty, x_pos in difficulty_labels:
            pygame.draw.rect(WIN, (150, 150, 150), (x_pos - bw / 2, 350, bw, bh))
            label = FONT.render(difficulty, 1, (255, 255, 255))
            WIN.blit(label, (x_pos - label.get_width() / 2, 350 + bh / 2 - label.get_height() / 2))

        WIN.blit(expert_label, (1, 1))
        WIN.blit(title_label, (SCREEN_WIDTH/2 - title_label.get_width()/2, 200))
        pygame.draw.rect(WIN, (150, 150, 150),
                         (SCREEN_WIDTH / 2 - leaderboard_label.get_width() / 2 - 10, 450,
                          leaderboard_label.get_width() + 20, leaderboard_label.get_height() + 10))
        WIN.blit(leaderboard_label, (SCREEN_WIDTH / 2 - leaderboard_label.get_width() / 2, 450))

        pygame.draw.rect(WIN, (150, 150, 150),
                         (SCREEN_WIDTH / 2 - quit_label.get_width() / 2 - 10, 550,
                          quit_label.get_width() + 20, quit_label.get_height() + 10))
        WIN.blit(quit_label, (SCREEN_WIDTH / 2 - quit_label.get_width() / 2, 550))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if (350 <= y <= 350 + easy_label.get_height() and
                        (SCREEN_WIDTH / 4 - easy_label.get_width() / 2) <= x <=
                        (SCREEN_WIDTH / 4 + easy_label.get_width() / 2)):
                    main("Easy")
                elif (350 <= y <= 350 + medium_label.get_height() and
                      (SCREEN_WIDTH / 2 - medium_label.get_width() / 2) <= x <=
                      (SCREEN_WIDTH / 2 + medium_label.get_width() / 2)):
                    main("Medium")
                elif (350 <= y <= 350 + hard_label.get_height() and
                      (3 * SCREEN_WIDTH / 4 - hard_label.get_width() / 2) <= x <= (
                              3 * SCREEN_WIDTH / 4 + hard_label.get_width() / 2)):
                    main("Hard")
                elif (0 <= y <= 0 + expert_label.get_height() and
                      0 <= x <= expert_label.get_width()):
                    main("Expert")
                if (450 <= y <= 450 + leaderboard_label.get_height() and
                        (SCREEN_WIDTH/2 - leaderboard_label.get_width()/2) <= x
                        <= (SCREEN_WIDTH/2 + leaderboard_label.get_width()/2)):
                    leaderboard_screen()
                if (550 <= y <= 550 + quit_label.get_height() and
                        (SCREEN_WIDTH/2 - quit_label.get_width()/2) <= x <=
                        (SCREEN_WIDTH/2 + quit_label.get_width()/2)):
                    pygame.quit()
                    quit()


def show_pause_screen():
    global paused
    paused_font = pygame.font.SysFont("comic sans", 60)
    pause_label = paused_font.render("Paused", 1, (255, 255, 255))
    WIN.blit(pause_label, (SCREEN_WIDTH/2 - pause_label.get_width()/2, SCREEN_HEIGHT/2 - pause_label.get_height()/2))
    pygame.display.update()
    # Keep the game paused until 'p' is pressed again
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    print("unpause")
                    return  # Exit the pause screen and continue the game


def leaderboard_screen():
    run = True
    current_difficulty = "Easy"
    button_width, button_height = 150, 50
    buttons = {
        "Easy": (SCREEN_WIDTH * 1 // 5 - button_width // 2, SCREEN_HEIGHT - 100, button_width, button_height),
        "Medium": (SCREEN_WIDTH * 2 // 5 - button_width // 2, SCREEN_HEIGHT - 100, button_width, button_height),
        "Hard": (SCREEN_WIDTH * 3 // 5 - button_width // 2, SCREEN_HEIGHT - 100, button_width, button_height),
        "Expert": (SCREEN_WIDTH * 4 // 5 - button_width // 2, SCREEN_HEIGHT - 100, button_width, button_height)
    }

    clock = pygame.time.Clock()

    while run:
        WIN.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                for difficulty, (bx, by, bw, bh) in buttons.items():
                    if bx <= x <= bx+bw and by <= y <= by+bh:
                        current_difficulty = difficulty
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
        display_leaderboard(current_difficulty)

        for difficulty, (bx, by, bw, bh) in buttons.items():
            pygame.draw.rect(WIN, (150, 150, 150), (bx, by, bw, bh))
            label = FONT.render(difficulty, 1, (0, 0, 0) if current_difficulty == difficulty else (255, 255, 255))
            WIN.blit(label, (bx + bw // 2 - label.get_width() // 2, by + bh // 2 - label.get_height() // 2))

        pygame.display.update()
        clock.tick(3)


def main(difficulty="difficulty"):

    print(f"Difficulty is: {difficulty}")
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"Invalid difficulty: {difficulty}")
    global last_pause_time
    star_vel = DIFFICULTIES[difficulty]['star_vel']
    star_add_increment = DIFFICULTIES[difficulty]['star_spawn_rate']
    star_vel_increment = DIFFICULTIES[difficulty]['star_vel_increment']
    global PLAYER_VEL
    PLAYER_VEL = DIFFICULTIES[difficulty]['player_vel']
    run = True
    global paused
    player = PLAYER_IMAGE.get_rect(topleft=(450, SCREEN_HEIGHT - PLAYER_HEIGHT))

    clock = pygame.time.Clock()
    start_time = time.time()
    stars_passed = 0
    star_count = 0
    stars = []
    hit = False

    while run:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    last_pause_time = current_time
                    if paused:
                        show_pause_screen()
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    return

        if not paused:
            star_count += clock.tick(60)
            score = time.time() - start_time

            if star_count > star_add_increment:  # Add stars every star_add_increment
                for _ in range(8):  # Add 8 stars every star_add_increment
                    star = Star(star_vel)
                    stars.append(star)

                star_add_increment = max(200, star_add_increment - 50)  # Decrease star_add_increment by 50 every time
                star_count = 0  # Reset star_count

            keys = pygame.key.get_pressed()
            handle_movement(keys, player)

            for star in stars[:]:  # Iterate through a copy of the stars list
                star.move()
                if star.y > SCREEN_HEIGHT:
                    stars_passed += 1  # Increase stars_passed by 1
                    stars.remove(star)
                elif star.y + STAR_HEIGHT >= player.y and collide(star, player):
                    stars.remove(star)
                    hit = True
                    break
                if stars_passed > 0 and stars_passed % 8 == 0:  # Increase star velocity every 8 stars
                    for s in stars:  # Increase star velocity for all stars
                        s.velocity += star_vel_increment  # Increase star velocity by 0.3 every 8 stars
                    stars_passed = 0  # Reset stars_passed
            if hit:  # If the player was hit by a star
                player_name = get_player_name()  # Get the player's name
                update_leaderboard(player_name, round(score), difficulty)  # Update the leaderboard
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        main(difficulty)
                        return
                    if keys[pygame.K_ESCAPE]:
                        main_menu()
                        return

                    lost_text = FONT.render("YOU LOST!", 1, (255, 255, 255))
                    restart_text = FONT.render("PRESS SPACE TO RESTART", 1, (255, 255, 255))
                    return_to_menu_text = FONT.render("PRESS ESC TO RETURN TO MAIN MENU", 1, (255, 255, 255))
                    final_score_text = FONT.render(f"Final Score: {round(score)}", 1, (255, 255, 255))
                    WIN.blit(BG, (0, 0))
                    WIN.blit(pygame.transform.rotozoom(PLAYER_IMAGE, 0, 4), (SCREEN_WIDTH/2-PLAYER_WIDTH*2, 175))
                    WIN.blit(final_score_text, (SCREEN_WIDTH / 2 - final_score_text.get_width() / 2,
                                                SCREEN_HEIGHT / 2 + 100))
                    WIN.blit(lost_text, (SCREEN_WIDTH / 2 - lost_text.get_width() / 2,
                                         SCREEN_HEIGHT / 2 - lost_text.get_height() / 2))
                    WIN.blit(restart_text, (SCREEN_WIDTH / 2 - restart_text.get_width() / 2, 650))
                    WIN.blit(return_to_menu_text, (SCREEN_WIDTH/2 - return_to_menu_text.get_width()/2, 20))
                    pygame.display.update()

            draw(player, stars, score)

    pygame.quit()


if __name__ == "__main__":
    main_menu()
