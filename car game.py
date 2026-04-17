import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 700
FPS = 60
ROAD_WIDTH = 2000
SEGMENT_LENGTH = 200
CAMERA_HEIGHT = 1000
CAMERA_DEPTH = 1 / 150
FIELD_OF_VIEW = 100
SEGMENTS = 500

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
ROAD_GRAY = (105, 105, 105)
RUMBLE_WHITE = (255, 255, 255)
RUMBLE_DARK = (255, 255, 255)
GRASS_GREEN = (16, 200, 16)
SKY_BLUE = (86, 194, 250)

class Car:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.dx = 0
        self.dz = 0
        self.speed = 0
        self.max_speed = 200
        self.acceleration = 0.5
        self.brake_force = 0.7
        self.off_road_decel = -0.01
        self.decel = -0.005
        self.centrifugal_force = 0.0002
        self.width = 80
        self.break_angle = 15
        
    def update(self, dt, road_width, curves):
        # Input handling
        keys = pygame.key.get_pressed()
        
        # Acceleration/Braking
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed += self.acceleration * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed -= self.brake_force * dt
        
        # Steering
        steer = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            steer = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            steer = 1
        
        # Speed limits
        self.speed = max(-self.max_speed/2, min(self.speed, self.max_speed))
        
        # Lateral friction
        if self.dx > 1:
            self.dx -= 0.1 * dt
        elif self.dx < -1:
            self.dx += 0.1 * dt
        
        # Steering
        self.dx = steer * self.max_speed/2 * 0.03 * dt
        
        # Update position
        self.x -= self.dx * dt
        self.z += self.speed * dt
        
        # Road boundaries
        road_w = road_width * 0.5
        if self.x > road_w:
            self.x = road_w
            self.dx = 0
        elif self.x < -road_w:
            self.x = -road_w
            self.dx = 0

class Segment:
    def __init__(self, index):
        self.index = index
        self.p1 = None
        self.p2 = None
        self.color_grass = GRASS_GREEN
        self.color_rumble = RUMBLE_WHITE
        self.color_road = ROAD_GRAY
        self.color_rumble_dark = RUMBLE_DARK
        self.curve = 0
        self.y = 0
        self.poles = {}

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Realistic 3D Car Racing Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        self.car = Car()
        self.segments = []
        self.cars = []
        self.background = None
        self.hill = 0
        self.position = 0
        self.player_z = CAMERA_HEIGHT
        
