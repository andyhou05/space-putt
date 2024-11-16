import pygame
from models.projectile import Projectile
from models.planet import Planet
from models.holes import Hole
from helper import *
from models.start import Start

# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Space Putt")
clock = pygame.time.Clock()
running = True

bg = pygame.image.load("pictures/hackaton_background.png")
bg = pygame.transform.scale(bg, (800, 600))

# Explosion gif
explosion = pygame.image.load("pictures/explosion.gif")
explosion = pygame.transform.scale(explosion, (50, 50))

# Store the projectile objects
projectiles = []

# Store the planet objects
planets = [Planet((400, 300), 50),Planet((200,100),50)]

# Store the holes
holes = [Hole((100,100),30),Hole((600,500),30)]

# Store starting positions
positions = [Start((500, 400)),Start((100,400))]

# Colors:
RED = (255, 0, 0)  # For planets
BLUE = (0, 0, 255) # For user body

# drag effect
last_pos = (0,0)
drawing = False
x = 0
y = 0
target_x = 0
target_y = 0
mouse_position = (0,0)

# Level_counter
level = 1





while running:
    # Poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Create a new projectile with every mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if event.pos[0] >= positions[level-1].position[0] and event.pos[0] <= positions[level-1].position[0]+200 and event.pos[1] >= positions[level-1].position[1] and event.pos[1] <= positions[level-1].position[1]+150:
                    projectile = Projectile(position = pygame.mouse.get_pos(), radius = 15)
                    projectiles.append(projectile)
                    drawing = True
                    last_pos = pygame.mouse.get_pos()
                    mouse_position = pygame.mouse.get_pos()
                    target_x, target_y = last_pos
                



        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                mouse_position = pygame.mouse.get_pos()
                x, y = mouse_position
                
        elif event.type == pygame.MOUSEBUTTONUP:


            # Calculate velocity based on length of drag, we use -1 index since the newest projectile will always be at the end of the projectiles list
            if len(projectiles) !=0:
                projectiles[-1].velocity = calculate_velocity(pygame.mouse.get_pos(), last_pos)


            drawing = False



    screen.blit(bg,(0,0))
    
    
    # Draw the planets
    planet = planets[level-1]
    pygame.draw.circle(screen, RED, planet.position, planet.radius)

    hole = holes[level-1]
    pygame.draw.circle(screen, "yellow", hole.position, hole.radius)


    # Draw the starting zone
    start_position = positions[level-1]
    pygame.draw.rect(screen, "Green", (start_position.position[0], start_position.position[1], 200, 150))


    # Draw all circles stored in the list
    for projectile in projectiles:
        pygame.draw.circle(screen, BLUE, projectile.position, projectile.radius)
        if projectile.velocity != 0:
            projectile.position = ((projectile.position[0] + projectile.velocity[0]/50), (projectile.position[1] + projectile.velocity[1]/50))
            projectile.velocity = (projectile.velocity[0] + gravitational_acceleration(projectile.position, planets[0])[0]), (projectile.velocity[1] + gravitational_acceleration(projectile.position, planets[0])[1])
        if distance_calc(projectile.position, planet.position) <= projectile.radius + planet.radius:
            projectiles.remove(projectile)

    if drawing:
        if last_pos != pygame.mouse.get_pos():
            drag_effect = pygame.draw.line(screen, "white", last_pos, mouse_position, 3)
            
    elif not drawing:
        if last_pos != mouse_position:
            # Slingshot animation
            diff_x = target_x - x
            x += diff_x / 3
            diff_y = target_y - y
            y += diff_y / 3
            drag_effect = pygame.draw.line(screen, "white", (x,y), last_pos, 3)
            mouse_position = (round(x),round(y))
    

    # Draw all circles stored in the list
    for projectile in projectiles:
        pygame.draw.circle(screen, BLUE, projectile.position, projectile.radius)
        if projectile.velocity != 0:
            projectile.position = ((projectile.position[0] + projectile.velocity[0]/50), (projectile.position[1] + projectile.velocity[1]/50))
            projectile.velocity = (projectile.velocity[0] + gravitational_acceleration(projectile.position, planets[0])[0]), (projectile.velocity[1] + gravitational_acceleration(projectile.position, planets[0])[1])
        if distance_calc(projectile.position,planet.position) <= projectile.radius + planet.radius:
            projectiles.remove(projectile)
        if distance_calc(projectile.position,hole.position) <= projectile.radius + hole.radius:
            projectiles.clear()
            if len(planets) == level:
                print("u finished")
            else:
                level += 1

    # title of level
    font = pygame.font.SysFont("Arial", 35)
    text = f"Level {level}"
    text_surface = font.render(text, True, "white")
    screen.blit(text_surface,(350,50))

    # Flip the display to put your work on the screen
    pygame.display.flip()

    # Limit FPS to 60
    clock.tick(60)

pygame.quit()
