import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((720, 720))
clock = pygame.time.Clock()
running = True


x = -100
speed = 300
fps = 200
N = 20
size = (N+2) * (N+2)

u = [0 for _ in range(size)]
v = [0 for _ in range(size)]
u_prev = [0 for _ in range(size)]
v_prev = [0 for _ in range(size)]

dens = [0 for _ in range(size)]
dens_prev = [0 for _ in range(size)]

def IX(x, y):
    return x + (N+2) * y

h = 1.0 / N


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE
    # draw a circle
    pygame.draw.circle(screen, "red", (x, 360), 100)
    x += speed / fps
    if x > 820:
        x = -100
    
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(fps)  # limits FPS to 60

pygame.quit()