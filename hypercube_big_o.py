import pygame
import numpy as np
import itertools
import sys

# Initialize Pygame
pygame.init()

# Window settings (wide enough for labels + centered visualizations)
WIDTH = 1000
HEIGHT = 780  # 6 panels stacked vertically
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Big O Hypercube Rotator - Beating the Squiggly Lines")
clock = pygame.time.Clock()

# Big O labels and their corresponding hypercube dimensions (top = simplest, bottom = most complex)
visuals = [
    ("O(1)", 2),          # rotating square
    ("O(log n)", 3),      # rotating wireframe cube
    ("O(n)", 4),          # rotating tesseract
    ("O(n log n)", 5),    # rotating 5D cube
    ("O(n²)", 6),         # rotating 6D cube
    ("O(2ⁿ)", 7),         # rotating 7D cube
]

class Hypercube:
    def __init__(self, dim: int):
        self.dim = dim
        # Generate all 2^dim vertices: every combination of ±1 in dim dimensions
        self.vertices = np.array(list(itertools.product([-1.0, 1.0], repeat=dim)))
        
        # Generate edges: connect vertices that differ in exactly one coordinate
        self.edges = []
        n = len(self.vertices)
        for i in range(n):
            for j in range(i + 1, n):
                if np.sum(np.abs(self.vertices[i] - self.vertices[j])) == 2.0:
                    self.edges.append((i, j))

    def get_rotated_and_projected(self, t: float):
        # Build composite rotation matrix (same as before)
        rot_mat = np.eye(self.dim)
        num_rots = 0
        max_rots = 8
        for i in range(self.dim):
            for j in range(i + 1, self.dim):
                if num_rots >= max_rots:
                    break
                theta = t * (0.35 + 0.07 * (i + j))
                c, s = np.cos(theta), np.sin(theta)
                r = np.eye(self.dim)
                r[i, i] = c
                r[i, j] = -s
                r[j, i] = s
                r[j, j] = c
                rot_mat = rot_mat @ r
                num_rots += 1
            if num_rots >= max_rots:
                break

        rotated = (rot_mat @ self.vertices.T).T

        # ------------------ Improved chained perspective projection ------------------
        proj = rotated.copy()
        current_dim = self.dim
        base_distance = 6.0          # increased a bit → fewer points go behind camera
        epsilon = 1e-4
        min_scale = 0.1              # prevent explosion / total disappearance

        while current_dim > 2:
            depth_coord = proj[:, current_dim - 1]
        
            # Prevent division by zero or negative → push points slightly in front
            denom = base_distance - depth_coord
            denom = np.maximum(denom, epsilon)   # avoid ≤ 0
        
            scale = base_distance / denom
            scale = np.maximum(scale, min_scale) # cap explosion
        
            # Apply scaling only to the remaining lower dimensions
            proj[:, :current_dim - 1] *= scale[:, np.newaxis]
        
            current_dim -= 1

        return proj[:, :2]


# Create one hypercube per Big O
hypercubes = [Hypercube(d) for _, d in visuals]

# Font for labels
font = pygame.font.SysFont("Arial", 32, bold=True)

# Main animation loop
running = True
time = 0.0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((8, 8, 18))  # deep space background

    panel_height = HEIGHT // len(visuals)

    for idx, ((label, _), hc) in enumerate(zip(visuals, hypercubes)):
        y_offset = idx * panel_height

        # Big O label on the left
        text = font.render(label, True, (180, 255, 200))
        screen.blit(text, (30, y_offset + 25))

        # Center of this panel
        center_x = WIDTH // 2
        center_y = y_offset + panel_height // 2

        # Rotate + project
        proj_2d = hc.get_rotated_and_projected(time)

        # Auto-scale to nicely fill the panel (higher dimensions stay readable)
        if len(proj_2d) > 0:
            max_extent = np.max(np.abs(proj_2d)) + 1e-6
            scale = min(WIDTH * 0.23, panel_height * 0.37) / max_extent
            screen_points = proj_2d * scale + np.array([center_x, center_y])

            # Draw wireframe edges (bright cyan)
            for edge in hc.edges:
                p1 = tuple(screen_points[edge[0]].astype(int))
                p2 = tuple(screen_points[edge[1]].astype(int))
                pygame.draw.line(screen, (0, 220, 255), p1, p2, 2)

            # Draw vertices (glowing dots)
            for p in screen_points:
                pygame.draw.circle(screen, (255, 255, 100), tuple(p.astype(int)), 3)

    pygame.display.flip()
    time += 0.028  # smooth rotation speed (tweak if you want faster/slower)
    clock.tick(60)

pygame.quit()
sys.exit()
