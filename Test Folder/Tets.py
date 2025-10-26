import pygame
import random
import time
# Initialize Pygame
pygame.init()
# Screen dimensions and colors
display_width = 800
display_height = 600
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 200, 0)
blue = (0, 0, 255)
# Set up display
game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Car Racing Game")
clock = pygame.time.Clock()
# Load assets
car_img = pygame.image.load('car.png') # Replace with your car image path
car_width = 50
# Function to display obstacles
def obstacles(obs_x, obs_y, obs_w, obs_h, color):
   pygame.draw.rect(game_display, color, [obs_x, obs_y, obs_w, obs_h])
# Function to display the car
def car(x, y):
   game_display.blit(car_img, (x, y))
# Display crash message
def crash():
   font = pygame.font.Font('freesansbold.ttf', 75)
   text_surface = font.render("You Crashed!", True, red)
   text_rect = text_surface.get_rect(center=(display_width / 2, display_height / 2))
   game_display.blit(text_surface, text_rect)
   pygame.display.update()
   time.sleep(2)
# Main game loop
def game_loop():
   x = display_width * 0.45
   y = display_height * 0.8
   x_change = 0
   obs_start_x = random.randrange(100, display_width - 100)
   obs_start_y = -600
   obs_speed = 7
   obs_width = 50
   obs_height = 100
   game_exit = False
   while not game_exit:
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               pygame.quit()
               quit()
           if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_LEFT:
                   x_change = -5
               elif event.key == pygame.K_RIGHT:
                   x_change = 5
           if event.type == pygame.KEYUP:
               if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                   x_change = 0
       x += x_change
       # Fill screen and draw elements
       game_display.fill(white)
       obstacles(obs_start_x, obs_start_y, obs_width, obs_height, black)
       obs_start_y += obs_speed
       car(x, y)
       # Check for collisions or boundaries
       if x > display_width - car_width or x < 0:
           crash()
           game_loop()
       if obs_start_y > display_height:
           obs_start_y = -obs_height
           obs_start_x = random.randrange(100, display_width - 100)
       if y < obs_start_y + obs_height:
           if x > obs_start_x and x < obs_start_x + obs_width or x + car_width > obs_start_x and x + car_width < obs_start_x + obs_width:
               crash()
               game_loop()
       pygame.display.update()
       clock.tick(60)
game_loop()
pygame.quit()
quit()