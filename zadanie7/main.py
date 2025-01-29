import pygame
import numpy as np
import random
import time

# Parametry mostu
width, height = 800, 920
num_points_x = 20
num_points_y = 6
spacing = width // (num_points_x + 1)
gravity = np.array([0, 0.5])
k = 0.2  # Stała sprężystości
current_time = 0  # Zmienna do śledzenia czasu życia kulek

# Inicjalizacja punktów mostu
points = [
    [np.array([j * spacing + spacing, i * 30 + 100], dtype=np.float64) for j in range(num_points_x)]
    for i in range(num_points_y)
]
old_points = [[p.copy() for p in row] for row in points]

# Połączenia sprężynowe
springs = []
for i in range(num_points_y):
    for j in range(num_points_x - 1):
        springs.append((i, j, i, j + 1))  # Poziome połączenia
for i in range(num_points_y - 1):
    for j in range(num_points_x):
        springs.append((i, j, i + 1, j))  # Pionowe połączenia

# Stałe punkty na końcach mostu
fixed_points = {(0, 0), (0, num_points_x - 1)}

# Zmienna do obsługi interakcji
selected_point = None



class Ball:
    def __init__(self, position, velocity, radius=35, restitution=0.8):
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.radius = radius
        self.restitution = restitution
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.creation_time = time.time()

    def update(self):
        self.velocity += gravity
        self.position += self.velocity

    def handle_collision(self, points):
        for i in range(num_points_y):
            for j in range(num_points_x):
                p = points[i][j]
                if np.linalg.norm(p - self.position) < self.radius:
                    # Jeśli kula dotknie mostu, odbija się
                    normal = (self.position - p) / np.linalg.norm(self.position - p)
                    self.velocity -= 2 * np.dot(self.velocity, normal) * normal
                    self.velocity *= self.restitution

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position.astype(int), self.radius)

    def is_alive(self):
        return time.time() - self.creation_time < 7



def create_balls():
    balls = []
    radius = random.randint(20, 40)
    velocity = [random.uniform(-1, 1), random.uniform(2, 5)]
    position = [random.randint(0, width), 50]
    balls.append(Ball(position=position, velocity=velocity, radius=radius))
    return balls


last_ball_time = time.time()


def handle_mouse():
    global selected_point
    mouse_pos = np.array(pygame.mouse.get_pos(), dtype=np.float64)
    if pygame.mouse.get_pressed()[0]:
        if selected_point is None:
            for i in range(num_points_y):
                for j in range(num_points_x):
                    if np.linalg.norm(points[i][j] - mouse_pos) < 15:
                        selected_point = (i, j)
                        break
        if selected_point is not None:
            points[selected_point[0]][selected_point[1]] = mouse_pos
    else:
        selected_point = None


def apply_gravity_to_bridge():
    for ball in balls:
        if ball.is_alive():
            # Przemieszczamy most w dół w zależności od pozycji kuli
            for i in range(num_points_y):
                for j in range(num_points_x):
                    dist = np.linalg.norm(points[i][j] - ball.position)
                    if dist < ball.radius + 10:
                        displacement = (ball.radius + 10 - dist) * 0.1
                        points[i][j] += np.array([0, displacement])

def apply_verlet():
    for i in range(num_points_y):
        for j in range(num_points_x):
            if (i, j) not in fixed_points:
                velocity = points[i][j] - old_points[i][j]
                old_points[i][j] = points[i][j].copy()
                points[i][j] += velocity + gravity


def apply_constraints():
    for i1, j1, i2, j2 in springs:
        p1, p2 = points[i1][j1], points[i2][j2]
        delta = p2 - p1
        dist = np.linalg.norm(delta)
        if dist == 0:
            continue
        correction = (dist - spacing) * k * (delta / dist)
        if (i1, j1) not in fixed_points:
            points[i1][j1] += correction
        if (i2, j2) not in fixed_points:
            points[i2][j2] -= correction


# Funkcja rysująca wszystko na ekranie
def draw():
    screen.fill((0, 0, 0))

    # Rysowanie mostu
    for i1, j1, i2, j2 in springs:
        pygame.draw.line(screen, (255, 255, 255), points[i1][j1], points[i2][j2], 2)

    for ball in balls:
        if ball.is_alive():
            ball.draw(screen)

    pygame.display.flip()


pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

balls = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = time.time()
    if current_time - last_ball_time >= 5:
        balls += create_balls()
        last_ball_time = current_time

    for ball in balls[:]:
        ball.update()
        ball.handle_collision(points)
        if not ball.is_alive():
            balls.remove(ball)

    apply_verlet()
    apply_constraints()
    apply_gravity_to_bridge()  # Zastosowanie zakrzywienia mostu przez kulki
    handle_mouse()  # Obsługa myszy
    draw()
    clock.tick(60)

pygame.quit()
