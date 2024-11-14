import pygame
import random
import numpy as np
import moviepy.editor as mpy

N = 1000
width, height = 800, 600
G = 400
cx, cy = width / 2, height / 2
dt = 1
central_radius = 10
attraction_radius = 75

pygame.init()
screen = pygame.display.set_mode((width, height))
background_color = (0, 0, 0)
center_color = (255, 255, 255)

x = np.random.uniform(0, width, N)
y = np.random.uniform(0, height, N)
vx = np.random.uniform(-1, 1, N)
vy = np.random.uniform(-1, 1, N)
radii = np.random.uniform(2, 5, N)

def generate_warm_color():
    red = random.randint(180, 255)
    green = random.randint(100, 200)
    blue = random.randint(0, 60)
    return (red, green, blue)

colors = [generate_warm_color() for _ in range(N)]

frames = []
running = True
clock = pygame.time.Clock()
frame_count = 0
max_frames = 600

while running and frame_count < max_frames:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(background_color)
    pygame.draw.circle(screen, center_color, (int(cx), int(cy)), central_radius)

    dx = cx - x
    dy = cy - y
    r = np.sqrt(dx**2 + dy**2)
    within_radius = r < attraction_radius
    Fx = np.zeros(N)
    Fy = np.zeros(N)
    Fx[within_radius] = G * dx[within_radius] / r[within_radius]**3
    Fy[within_radius] = G * dy[within_radius] / r[within_radius]**3

    vx += Fx * dt
    vy += Fy * dt
    x += vx * dt
    y += vy * dt

    # Odbicie od krawędzi z uwzględnieniem promienia dysków
    for i in range(N):
        if x[i] - radii[i] < 0:       # Lewa krawędź
            x[i] = radii[i]
            vx[i] *= -1
        elif x[i] + radii[i] > width:  # Prawa krawędź
            x[i] = width - radii[i]
            vx[i] *= -1

        if y[i] - radii[i] < 0:       # Górna krawędź
            y[i] = radii[i]
            vy[i] *= -1
        elif y[i] + radii[i] > height: # Dolna krawędź
            y[i] = height - radii[i]
            vy[i] *= -1

    for i in range(N):
        pygame.draw.circle(screen, colors[i], (int(x[i]), int(y[i])), int(radii[i]))

    pygame.display.flip()
    clock.tick(30)
    frame_count += 1

    frame_data = pygame.surfarray.array3d(screen)
    frames.append(np.rot90(frame_data))

pygame.quit()

clip = mpy.ImageSequenceClip(frames, fps=30)
clip.write_videofile("simulation.mp4", codec="libx264")
