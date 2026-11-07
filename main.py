import pygame
import serial

pygame.init()

WIDTH = 800 #window width, total x location can't exceed 
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Distance Sensor Control")

arduino = serial.Serial("COM3", 9600)

player_x = 0 #start position to the left - do we need to make a player object
#maybe we should partition the space so the movement is smoother? or avergage the readings 

clock = pygame.time.Clock()

running = True
count_readings = 0 #for averaging
reading_max = 3 #avg per 5 readings - make it slower and smoother
total_dist = 0
avg_distance = 0
avg_incr =  0
target_x = 0

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if arduino.in_waiting: #if there is data to be read from arduino
        try:
            distance = float(arduino.readline().decode().strip())
            total_dist +=distance-4  #raw value, push to left 
            count_readings+=1 #increment readings
            

        except:
            pass

    if count_readings >= reading_max:
        avg_distance = total_dist / reading_max
        target_x = avg_distance * 50
        count_readings = 0
        total_dist = 0


    player_x += (target_x - player_x) * 0.15 #distance between current player and target 
    player_x = max(0, min(player_x, WIDTH - 50)) # print current avg, gets rid of noise
    print(player_x)
    screen.fill((0, 0, 0))

    pygame.draw.rect(
        screen,
        (0, 255, 0),
        (player_x, 150, 50, 50) # draw at 150 px from the top 
    )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()