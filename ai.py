import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Simulation parameters
N = 64  # grid size
iter = 4  # solver iterations
SCALE = 8  # display scale
width, height = N*SCALE, N*SCALE

# Set up display
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Red Fluid Simulation")

class FluidSim:
    def __init__(self, size):
        self.size = size
        self.dt = 0.1
        self.diff = 0.0001
        self.visc = 0.0001
        
        # Arrays for density and velocity
        self.density = np.zeros((size, size))
        self.Vx = np.zeros((size, size))
        self.Vy = np.zeros((size, size))
        self.Vx0 = np.zeros((size, size))
        self.Vy0 = np.zeros((size, size))
    
    def add_density(self, x, y, amount):
        self.density[int(x), int(y)] += amount
    
    def add_velocity(self, x, y, amountX, amountY):
        self.Vx[int(x), int(y)] += amountX
        self.Vy[int(x), int(y)] += amountY
    
    def diffuse(self, b, x, x0):
        a = self.dt * self.diff * (self.size - 2) * (self.size - 2)
        self.lin_solve(b, x, x0, a, 1 + 6 * a)
    
    def lin_solve(self, b, x, x0, a, c):
        for k in range(iter):
            for i in range(1, self.size - 1):
                for j in range(1, self.size - 1):
                    x[i, j] = (x0[i, j] + a * (x[i+1, j] + x[i-1, j] + 
                                              x[i, j+1] + x[i, j-1])) / c
            self.set_bnd(b, x)
    
    def project(self, velocX, velocY, p, div):
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                div[i, j] = -0.5 * (
                    velocX[i+1, j] - velocX[i-1, j] + 
                    velocY[i, j+1] - velocY[i, j-1]
                ) / self.size
                p[i, j] = 0

        self.set_bnd(0, div)
        self.set_bnd(0, p)
        self.lin_solve(0, p, div, 1, 6)
        
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                velocX[i, j] -= 0.5 * (p[i+1, j] - p[i-1, j]) * self.size
                velocY[i, j] -= 0.5 * (p[i, j+1] - p[i, j-1]) * self.size
                
        self.set_bnd(1, velocX)
        self.set_bnd(2, velocY)
    
    def advect(self, b, d, d0, velocX, velocY):
        dt0 = self.dt * (self.size - 2)
        
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                x = i - dt0 * velocX[i, j]
                y = j - dt0 * velocY[i, j]
                
                if x < 0.5:
                    x = 0.5
                if x > self.size - 1.5:
                    x = self.size - 1.5
                i0 = int(x)
                i1 = i0 + 1
                
                if y < 0.5:
                    y = 0.5
                if y > self.size - 1.5:
                    y = self.size - 1.5
                j0 = int(y)
                j1 = j0 + 1
                
                s1 = x - i0
                s0 = 1 - s1
                t1 = y - j0
                t0 = 1 - t1
                
                d[i, j] = s0 * (t0 * d0[i0, j0] + t1 * d0[i0, j1]) + \
                         s1 * (t0 * d0[i1, j0] + t1 * d0[i1, j1])
                
        self.set_bnd(b, d)
    
    def set_bnd(self, b, x):
        for i in range(1, self.size - 1):
            if b == 1:
                x[0, i] = -x[1, i]
                x[self.size-1, i] = -x[self.size-2, i]
            else:
                x[0, i] = x[1, i]
                x[self.size-1, i] = x[self.size-2, i]
                
            if b == 2:
                x[i, 0] = -x[i, 1]
                x[i, self.size-1] = -x[i, self.size-2]
            else:
                x[i, 0] = x[i, 1]
                x[i, self.size-1] = x[i, self.size-2]
        
        x[0, 0] = 0.5 * (x[1, 0] + x[0, 1])
        x[0, self.size-1] = 0.5 * (x[1, self.size-1] + x[0, self.size-2])
        x[self.size-1, 0] = 0.5 * (x[self.size-2, 0] + x[self.size-1, 1])
        x[self.size-1, self.size-1] = 0.5 * (x[self.size-2, self.size-1] + x[self.size-1, self.size-2])
    
    def step(self):
        # Velocity step
        self.diffuse(1, self.Vx0, self.Vx)
        self.diffuse(2, self.Vy0, self.Vy)
        
        self.project(self.Vx0, self.Vy0, self.Vx, self.Vy)
        
        self.advect(1, self.Vx, self.Vx0, self.Vx0, self.Vy0)
        self.advect(2, self.Vy, self.Vy0, self.Vx0, self.Vy0)
        
        self.project(self.Vx, self.Vy, self.Vx0, self.Vy0)
        
        # Density step
        self.diffuse(0, self.Vx0, self.density)
        self.advect(0, self.density, self.Vx0, self.Vx, self.Vy)

# Create fluid simulation instance
fluid = FluidSim(N)

# Main game loop
running = True
prev_mouse = None
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Get mouse position and add density/velocity
    mouse_pos = pygame.mouse.get_pos()
    mouse_x, mouse_y = mouse_pos[0] // SCALE, mouse_pos[1] // SCALE
    
    if pygame.mouse.get_pressed()[0]:  # Left mouse button
        if prev_mouse is not None:
            dx = (mouse_x - prev_mouse[0]) * 2
            dy = (mouse_y - prev_mouse[1]) * 2
            fluid.add_velocity(mouse_x, mouse_y, dx, dy)
        fluid.add_density(mouse_x, mouse_y, 100)
        prev_mouse = (mouse_x, mouse_y)
    else:
        prev_mouse = None
    
    # Update simulation
    fluid.step()
    
    # Draw fluid with white background
    screen.fill((255, 255, 255))  # White background
    for i in range(N):
        for j in range(N):
            x = i * SCALE
            y = j * SCALE
            d = fluid.density[i, j]
            # Only draw if there's significant density
            if d > 0.1:  # Threshold to avoid drawing very faint pixels
                print(d * 255)
                red = min(255, int(d * 255))
                pygame.draw.rect(screen, (red, 0, 0),  # Pure red
                               (x, y, SCALE, SCALE))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()