import pygame
from models.projectile import Projectile
from models.planet import Planet
from models.obstacles import Obstacle
from models.holes import Hole
from helper import *
from models.start import Start
import sqlite3
from tkinter import*
import random
import time
import subprocess
import sys

# CREATING DATABASE
key = "Leaderboard.db"

connexion = sqlite3.connect(key)
cursor = connexion.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS leaderboard(id INTEGER PRIMARY KEY, nom TEXT, time FLOAT)")
connexion.commit()
connexion.close()



# main menu for connection
clear_list = []
fen = Tk()
fen.geometry("400x300")
fen.title("Space Putt")
police = ("Comic sans MS",20,"bold")
title = Label(fen,text="Welcome to Space Putt!",font=police)
title.place(relx=.5,rely=.2,anchor=CENTER)

#VALUES FOR DATABASE
id = None
name = ""
timer = 0
ids = []


def signup():
    global ids
    for items in clear_list:
        items.destroy()

    #Find ids already taken
    connexion = sqlite3.connect(key)
    cursor = connexion.cursor()
    result = cursor.execute("SELECT id FROM leaderboard")
    ids = [row[0] for row in result]
    connexion.commit()
    connexion.close()

    #give random id that doesnt exist
    id_generated = random.randint(1,1000)
    while id_generated in ids:
        id_generated = random.randint(1, 1000)

    info_id = Label(fen,text=f"your ID is {id_generated}\n Please enter your name!",font=police)
    info_id.place(relx=.5,rely=.3,anchor=CENTER)

    name = Entry(fen,font=police)
    name.place(relx=.5,rely=.6,anchor=CENTER)

    confirm = Button(fen,text="Confirm",font=police,command= lambda: database_info(id_generated,name.get()))
    confirm.place(relx=.5,rely=.8,anchor=CENTER)



def database_info(value_id,value_name):
    global id,name,timer
    data = (value_id,value_name,0)

    id = value_id
    name = value_name
    timer = 0
    connexion = sqlite3.connect(key)
    cursor = connexion.cursor()
    cursor.execute("INSERT INTO leaderboard(id,nom,time) VALUES (?,?,?)",data)

    connexion.commit()
    connexion.close()
    fen.destroy()

def confirmation(value_id,value_nom):
    global ids,id,name
    id = value_id
    nom = value_nom
    connexion = sqlite3.connect(key)
    cursor = connexion.cursor()
    result = cursor.execute("SELECT id FROM leaderboard")
    ids = [row[0] for row in result]
    connexion.commit()
    connexion.close()
    #name
    connexion = sqlite3.connect(key)
    cursor = connexion.cursor()
    result = cursor.execute("SELECT nom FROM leaderboard")
    names = [row[0] for row in result]
    connexion.commit()
    connexion.close()
    try:
        if int(value_id) in ids:
            pos = ids.index(int(value_id))
            if value_nom == names[pos]:
                fen.destroy()
        else:
            top = Toplevel(fen,width=200,height=200)
            texte = Label(top,text="Invalid identification")
            texte.pack()
    except ValueError:
        top = Toplevel(fen, width=200, height=200)
        texte = Label(top, text="Invalid identification")
        texte.pack()



def signin():

    for items in clear_list:
        items.destroy()
    info_id = Label(fen, text=f"Enter your ID and name", font=police)
    info_id.place(relx=.5, rely=.2, anchor=CENTER)
    police2 = ("Comic sans MS",15,"bold")

    ID = Entry(fen,font=police2)
    ID.place(relx=.6,rely=.4,anchor=CENTER)
    name = Entry(fen,font=police2)
    name.place(relx=.6,rely=.6,anchor=CENTER)

    ID_label = Label(fen,text="ID:",font=police2)
    ID_label.place(relx=.2,rely=.4,anchor=CENTER)
    nom_label = Label(fen,text="Name:",font=police2)
    nom_label.place(relx=.2,rely=.6,anchor=CENTER)

    confirm = Button(fen,text="Confirm",font=police,command=lambda:confirmation(ID.get(),name.get()))
    confirm.place(relx=.5,rely=.8,anchor=CENTER)






sign_in = Button(fen,text="Sign in",font=police,bg="gray",width=12,command=signin)
sign_in.place(relx=.5,rely=.5,anchor=CENTER)

create_account = Button(fen,text="Create account",font=police,bg="gray",command=signup)
create_account.place(relx=.5,rely=.8,anchor=CENTER)


clear_list.append(title)
clear_list.append(sign_in)
clear_list.append(create_account)


fen.mainloop()
# END OF TKINTER MENU

#START OF THE GAME


# VERIFYING PLAYER ID AND ALL INFO
if id is None:
    print("user needs to log in")
    exit()



# STARTING TIMER

start = time.time()




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
planets = [Planet((200,100),50),
           Planet((400, 300), 50),
           Planet((350, 300), 30),
           Planet((250, 270), 30),
           Planet((400, 200), 50)]

# Store the obstacles:
obstacles = [Obstacle((0,0), (0,0)),
             Obstacle((0, 0), (0, 0)),
             Obstacle((300, 300), (200, 300)),
             Obstacle((290, 270), (800, 270)),
             Obstacle((400, 260), (400, 600))]

# Store the holes
holes = [Hole((600,500),30),
         Hole((100,100),30),
         Hole((100, 300), 30),
         Hole((390,150),30),
         Hole((100,400),30)]

# Store starting positions
positions = [Start((100,400)),
             Start((500, 400)),
             Start((500, 250)),
             Start((290,420)),
             Start((500,400))]

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
# game counter
end = 0






while running:
    # Poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Create a new projectile with every mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if event.pos[0] >= positions[0].position[0] and event.pos[0] <= positions[0].position[0]+200 and event.pos[1] >= positions[0].position[1] and event.pos[1] <= positions[0].position[1]+150:
                    projectile = Projectile(position = pygame.mouse.get_pos(), radius = 25)
                    projectiles.append(projectile)
                    drawing = True
                    last_pos = pygame.mouse.get_pos()
                    mouse_position = pygame.mouse.get_pos()
                    target_x, target_y = last_pos




        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                mouse_position = pygame.mouse.get_pos()
                x, y = mouse_position
        elif drawing == True:
            if event.type == pygame.MOUSEBUTTONUP:
                # Calculate velocity based on length of drag, we use -1 index since the newest projectile will always be at the end of the projectiles list
                drawing = False


                if len(projectiles) !=0:
                    projectiles[-1].velocity = calculate_velocity(mouse_position, last_pos)

        elif drawing == True:
            if event.type == pygame.MOUSEBUTTONUP:
                # Calculate velocity based on length of drag, we use -1 index since the newest projectile will always be at the end of the projectiles list
                if len(projectiles) !=0:
                    projectiles[-1].velocity = calculate_velocity(mouse_position, last_pos)
                drawing = False




    screen.blit(bg,(0,0))









    # Draw the planets
    planet = planets[0]
    pygame.draw.circle(screen, "black", planet.position, planet.radius)
    my_image = pygame.image.load("pictures/sun.png")
    my_image = pygame.transform.scale(my_image, (planet.radius*2+50, planet.radius*2+50))
    circular_image = pygame.Surface((50, 50), pygame.SRCALPHA)
    image_rect = my_image.get_rect(center=planet.position)
    screen.blit(my_image, image_rect)

    hole = holes[0]
    circular_image = pygame.Surface((hole.radius*2 + 10, hole.radius*2 + 5), pygame.SRCALPHA)

    # Draw the circle on the transparent surface
    pygame.draw.circle(circular_image, (0, 0, 0, 0), (hole.radius + 5, hole.radius + 5), hole.radius)  # Transparent circle

    # Load and scale the image
    my_image = pygame.image.load("pictures/hole.png")
    my_image = pygame.transform.scale(my_image, (hole.radius*2 + 10, hole.radius*2 + 5))

    # Get the rect for positioning the image
    image_rect = my_image.get_rect(center=hole.position)

    # Blit the image onto the transparent surface
    circular_image.blit(my_image, (0, 0))

    # Blit the circular surface with transparency to the main screen
    screen.blit(circular_image, image_rect)

    # Draw the obstacles:
    obstacle = obstacles[0]
    obstacle_rect = pygame.draw.line(screen, "purple", obstacle.start_pos, obstacle.end_pos, obstacle.width)



    # Draw the starting zone
    start_position = positions[0]
    ellipse_width, ellipse_height = 200, 150

    # Create a transparent surface for the ellipse
    ellipse_surface = pygame.Surface((ellipse_width, ellipse_height), pygame.SRCALPHA)

    # Draw the ellipse on the transparent surface
    pygame.draw.ellipse(ellipse_surface, (255, 255, 255, 255), (0, 0, ellipse_width, ellipse_height))

    # Load and scale the image
    my_image = pygame.image.load("pictures/grass.png")
    my_image = pygame.transform.scale(my_image, (ellipse_width, ellipse_height))

    # Blit the image onto the ellipse surface
    ellipse_surface.blit(my_image, (0,0), special_flags=pygame.BLEND_RGBA_MIN)

    # Draw the elliptical image onto the main screen
    ellipse_rect = ellipse_surface.get_rect(topleft=start_position.position)
    screen.blit(ellipse_surface, ellipse_rect)

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
            #mouse_position = (round(x),round(y))


    # Draw all circles stored in the list
    for projectile in projectiles:

        # IMAGE CONNECTED TO THE CIRCLE
        projectile_rect = pygame.draw.circle(screen,"light blue", projectile.position, projectile.radius)
        my_image = pygame.image.load("pictures/earth.png")
        my_image = pygame.transform.scale(my_image, (projectile.radius*2+10, projectile.radius*2+5))
        circular_image = pygame.Surface((1, 1), pygame.SRCALPHA)
        image_rect = my_image.get_rect(center=projectile.position)
        screen.blit(my_image, image_rect)

        if projectile_rect.colliderect(obstacle_rect):
            projectiles.remove(projectile)


        if projectile.velocity != 0:
            projectile.position = ((projectile.position[0] + projectile.velocity[0]/50), (projectile.position[1] + projectile.velocity[1]/50))
            projectile.velocity = (projectile.velocity[0] + gravitational_acceleration(projectile.position, planets[0])[0]), (projectile.velocity[1] + gravitational_acceleration(projectile.position, planets[0])[1])
        if distance_calc(projectile.position,planet.position) <= projectile.radius + planet.radius:
            projectiles.remove(projectile)

        if projectile.position[0] >= 850 or projectile.position[0] <= -50 or projectile.position[1] >= 650 or projectile.position[1] <=-50:
            projectiles.remove(projectile)
        if distance_calc(projectile.position,hole.position) <= projectile.radius + hole.radius:

            if len(planets) == 1:
                ending = 1
                projectiles.remove(projectile)
                print("u finished")
                end = time.time()
                calcul = end-start
                print(calcul)
                connexion = sqlite3.connect(key)
                cursor = connexion.cursor()
                results = cursor.execute("SELECT time FROM leaderboard")
                times = [row[0] for row in results]
                connexion.commit()
                connexion.close()
                connexion = sqlite3.connect(key)
                cursor = connexion.cursor()
                results1 = cursor.execute("SELECT id FROM leaderboard")
                ids = [row[0] for row in results1]
                connexion.commit()
                connexion.close()
                position = ids.index(int(id))
                best_i = 0
                for i in times:
                    if i < best_i:
                        best_i = i
                if calcul < best_i:
                    print("world record!")

                if calcul < times[position]:
                    times[position] = calcul
                    print("personal Best!")
                    connexion = sqlite3.connect(key)
                    cursor = connexion.cursor()
                    results1 = cursor.execute("UPDATE leaderboard SET time = (?) WHERE id = (?)",(calcul,id))
                    ids = [row[0] for row in results1]
                    connexion.commit()
                    connexion.close()
                pygame.quit()
                ################################################################# TOOOOOOOOO CHANGE
                question = input("Would you like to continue? ")
                if question == "yes":
                    subprocess.run([sys.executable] + sys.argv)
                else:
                    exit()





            else:
                projectiles.clear()
                obstacles.pop(0)
                planets.pop(0)
                holes.pop(0)
                positions.pop(0)
                level += 1
















    # title of level
    font = pygame.font.SysFont("Arial", 35)
    text = f"Level {level}"
    text_surface = font.render(text, True, "white")
    screen.blit(text_surface,(350,50))
    text = f"time: {(time.time()-start):.2f}"
    timer = font.render(text, True, "white")
    screen.blit(timer, (600, 50))
    # Flip the display to put your work on the screen
    pygame.display.flip()

    # Limit FPS to 60
    clock.tick(60)

pygame.quit()
