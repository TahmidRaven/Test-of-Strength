from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy
import random as rdm
import math
import time

 
window_w, window_h = 720, 480
fps, t1, t2 = 60, 0, 0
player_stance = 0  # red is 0, green is 1, blue is 2
pause = False
move_queue = [None]*10
m_count = 0
game_over = False

# Player position and movement
player_x = 360
player_y = 240
move_speed = 8

# Witch position and state
witch_x, witch_y = 100, 100
witch_alive = True

# Projectiles
class Projectile:
    def __init__(self, x, y, dx, dy, speed=3):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.radius = 5

projectiles = []
last_shot_time = 0
shoot_delay = 2  # Seconds between witch shots

# Define boundaries
min_x = 50
max_x = window_w - 50
min_y = 100
max_y = window_h - 50

def findZone(dy, dx):
    if dy >= 0 and dx >= 0:
        if abs(dx) >= abs(dy):
            line_zone = 0
        else:
            line_zone = 1
    elif dy >= 0 and dx < 0:
        if abs(dx) >= abs(dy):
            line_zone = 3
        else:
            line_zone = 2
    elif dy < 0 and dx < 0:
        if abs(dx) >= abs(dy):
            line_zone = 4
        else:
            line_zone = 5
    elif dy < 0 and dx >= 0:
        if abs(dx) >= abs(dy):
            line_zone = 7
        else:
            line_zone = 6
    return line_zone

def converttoZone0(x, y, z):
    if z == 0:
        return [x, y]
    elif z == 1:
        return [y, x]
    elif z == 2:
        return [y, -x]
    elif z == 3:
        return [-x, y]
    elif z == 4:
        return [-x, -y]
    elif z == 5:
        return [-y, -x]
    elif z == 6:
        return [-y, x]
    else:
        return [x, -y]

def converttoZone(x, y, z):
    if z == 0:
        return [x, y]
    elif z == 1:
        return [y, x]
    elif z == 2:
        return [-y, x]
    elif z == 3:
        return [-x, y]
    elif z == 4:
        return [-x, -y]
    elif z == 5:
        return [-y, -x]
    elif z == 6:
        return [y, -x]
    else:
        return [x, -y]

def mLine(x1, y1, x2, y2):
    dy = y2 - y1
    dx = x2 - x1
    glBegin(GL_POINTS)
    glVertex2f(x1, y1)
    glEnd()

    zone = findZone(dy, dx)
    converted_coords = converttoZone0(x1, y1, zone)
    x1_p, y1_p = converted_coords[0], converted_coords[1]
    converted_coords = converttoZone0(x2, y2, zone)
    x2_p, y2_p = converted_coords[0], converted_coords[1]
    dy_p = y2_p - y1_p
    dx_p = x2_p - x1_p
    d = 2 * dy_p - dx_p
    e_inc = 2 * dy_p
    ne_inc = 2 * dy_p - 2 * dx_p
    while x1_p != x2_p:
        if d <= 0:
            d += e_inc
            x1_p += 1
        else:
            d += ne_inc
            x1_p += 1
            y1_p += 1
        converted_coords = converttoZone(x1_p, y1_p, zone)
        x1, y1 = converted_coords[0], converted_coords[1]
        
        glBegin(GL_POINTS)
        glVertex2f(x1, y1)
        glEnd()

def mTriangle(x1, y1, x2, y2, x3, y3):
  
    mLine(x1, y1, x2, y2)
    mLine(x2, y2, x3, y3)
    mLine(x3, y3, x1, y1)
    
    min_x = min(x1, x2, x3)
    max_x = max(x1, x2, x3)
    min_y = min(y1, y2, y3)
    max_y = max(y1, y2, y3)
    
    # Scan each row
    for y in range(int(min_y), int(max_y) + 1):
        for x in range(int(min_x), int(max_x) + 1):
       
            d1 = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
            d2 = (x3 - x2) * (y - y2) - (y3 - y2) * (x - x2)
            d3 = (x1 - x3) * (y - y3) - (y1 - y3) * (x - x3)
            
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            
            if not (has_neg and has_pos):
                glBegin(GL_POINTS)
                glVertex2f(x, y)
                glEnd()

def mCircle(c_x, c_y, radius):
    d, x, y = 1 - radius, 0, radius
    circlePoints(x, y, c_x, c_y)
    while x < y:
        if d < 0:
            d += 2 * x + 3
            x += 1
        else:
            d += 2 * x - 2 * y + 5
            x += 1
            y -= 1
        circlePoints(x, y, c_x, c_y)

def circlePoints(x, y, cx, cy):
    glBegin(GL_POINTS)
    glVertex2f(x + cx, y + cy)
    glVertex2f(y + cx, x + cy)
    glVertex2f(y + cx, -x + cy)
    glVertex2f(x + cx, -y + cy)
    glVertex2f(-x + cx, -y + cy)
    glVertex2f(-y + cx, -x + cy)
    glVertex2f(-y + cx, x + cy)
    glVertex2f(-x + cx, y + cy)
    glEnd()

def iterate():
    glViewport(0, 0, window_w, window_h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, window_w, 0.0, window_h, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def stanceColor(stance):
    if stance == 0:
        glColor3f(1, 0, 0)  # Red - Hell stance
        return [1, 0, 0]
    elif stance == 1:
        glColor3f(0, 1, 0)  # Green - Earth stance
        return [0, 1, 0]
    elif stance == 2:
        glColor3f(0, 0, 1)  # Blue - Heaven stance
        return [0, 0, 1]

def draw_witch(x, y):
    # Witch body (dark purple)
    glColor3f(0.5, 0, 0.5)
    
 
    mTriangle(x, y + 30,  # Hat tip
             x - 15, y + 10,  # Hat base left
             x + 15, y + 10)  # Hat base right
    
    # Hat brim
    mLine(x - 20, y + 10, x + 20, y + 10)
    
    # Head
    mCircle(x, y, 10)
    
    # Robe  
    mTriangle(x, y - 10,
             x - 20, y - 40,
             x + 20, y - 40)
    
    # Arms
    mLine(x - 15, y - 20, x - 25, y - 10)  # Left arm
    mLine(x + 15, y - 20, x + 25, y - 10)  # Right arm

def check_sword_collision():
    global witch_alive
    if not witch_alive:
        return False
        
    #  sword hitbox  
    sword_tip_x = player_x + 15
    sword_tip_y = player_y + 7
    sword_base_x = player_x + 15
    sword_base_y = player_y - 25
    
    # Calculate distance from sword to witch
    distance_tip = math.sqrt((sword_tip_x - witch_x)**2 + (sword_tip_y - witch_y)**2)
    distance_base = math.sqrt((sword_base_x - witch_x)**2 + (sword_base_y - witch_y)**2)
    
    # If either part of the sword is close enough to the witch
    if distance_tip < 20 or distance_base < 20:
        witch_alive = False
        return True
    return False

def update_projectiles():
    global game_over
    # Update projectile positions
    for proj in projectiles[:]:
        proj.x += proj.dx * proj.speed
        proj.y += proj.dy * proj.speed
 
        if (proj.x < 0 or proj.x > window_w or 
            proj.y < 0 or proj.y > window_h):
            projectiles.remove(proj)
            continue
            
        # Check collision with player
        distance = math.sqrt((proj.x - player_x)**2 + (proj.y - player_y)**2)
        if distance < 20:  # P hit radius
            game_over = True

def witch_shoot():
    global last_shot_time
    current_time = time.time()
    
    if current_time - last_shot_time >= shoot_delay and witch_alive:
 
        dx = player_x - witch_x
        dy = player_y - witch_y
  
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            dx /= length
            dy /= length
            
        # Gen new projectile
        projectiles.append(Projectile(witch_x, witch_y, dx, dy))
        last_shot_time = current_time

def reset_game():
    global player_x, player_y, witch_x, witch_y, witch_alive, game_over, projectiles, player_stance
   
    player_x = 360
    player_y = 240
    # Reset witch
    witch_x = 100
    witch_y = 100
    witch_alive = True
     
    projectiles.clear()
     
    game_over = False
    
    player_stance = 0

def display():
    global player_x, player_y, player_stance, witch_x, witch_y
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 0)
    glLoadIdentity()
    iterate()
 
    if not game_over:
        stanceColor(player_stance)

        # Player 
        head_radius = 7
        mCircle(player_x, player_y, head_radius)
        mLine(player_x, player_y - head_radius, player_x, player_y - 30)
        mLine(player_x, player_y - 15, player_x - 10, player_y - 25)
        mLine(player_x - 10, player_y - 25, player_x - 15, player_y - 35)
        mLine(player_x, player_y - 15, player_x + 10, player_y - 25)
        mLine(player_x + 10, player_y - 25, player_x + 15, player_y - 35)
        mLine(player_x, player_y - 30, player_x - 7, player_y - 50)
        mLine(player_x - 7, player_y - 50, player_x - 10, player_y - 65)
        mLine(player_x, player_y - 30, player_x + 7, player_y - 50)
        mLine(player_x + 7, player_y - 50, player_x + 10, player_y - 65)
        mCircle(player_x - 15, player_y - 35, 2)
        mCircle(player_x + 15, player_y - 35, 2)
        mCircle(player_x - 10, player_y - 65, 2)
        mCircle(player_x + 10, player_y - 65, 2)
        
        # Sword
        mLine(player_x + 15, player_y - 35, player_x + 15, player_y - 25)
        mLine(player_x + 15, player_y - 25, player_x + 20, player_y - 25)
        mLine(player_x + 10, player_y - 25, player_x + 15, player_y - 25)
        mLine(player_x + 15, player_y - 25, player_x + 15, player_y)
        mLine(player_x + 10, player_y - 25, player_x + 10, player_y)
        mLine(player_x + 20, player_y - 25, player_x + 20, player_y)
        mLine(player_x + 10, player_y, player_x + 15, player_y + 7)
        mLine(player_x + 20, player_y, player_x + 15, player_y + 7)

    #  witch if alive
    if witch_alive:
        draw_witch(witch_x, witch_y)
    
    #  projectiles
    glColor3f(1, 0, 1)   
    for proj in projectiles:
        mCircle(int(proj.x), int(proj.y), proj.radius)
    
 
    if game_over:
        glColor3f(1, 0, 0)
 
        glRasterPos2f(window_w//2 - 40, window_h//2)
        for c in "GAME OVER":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
 
        glRasterPos2f(window_w//2 - 90, window_h//2 - 30)
        for c in "Press SPACE to restart":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))

    glutSwapBuffers()

def update(value):
    if not pause and not game_over:
        witch_shoot()
        update_projectiles()
        check_sword_collision()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)  # 60 FPS 


def keyboardListener(key, x, y):
    global pause, player_stance, game_over, move_queue, m_count, player_x, player_y
    
 
    if game_over and key == b' ': 
        reset_game()
        return
    
    if not pause and not game_over:
     
        if key == b'q':
            player_stance = 1
        elif key == b'e':
            player_stance = 2
        elif key == b'r':
            player_stance = 0
            
        # Movement
        elif key == b'w':
            if player_y + move_speed <= max_y:   
                player_y += move_speed
        elif key == b's':
            if player_y - move_speed >= min_y:   
                player_y -= move_speed
        elif key == b'a':
            if player_x - move_speed >= min_x:  
                player_x -= move_speed
        elif key == b'd':
            if player_x + move_speed <= max_x:
                player_x += move_speed
            
    glutPostRedisplay()

 
glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
glutInitWindowSize(window_w, window_h)
glutCreateWindow(b"Test of Strength")
glutDisplayFunc(display)
glutKeyboardFunc(keyboardListener)
glutTimerFunc(0, update, 0)
glutMainLoop()