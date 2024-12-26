from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy
import random as rdm

# Window and game state variables
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
move_speed = 5

# Enemy position (for demonstration purposes, enemies will be at fixed positions)
enemy_x, enemy_y = 100, 100
enemy_stance = 3  # Teal/Off-white color for enemies

# Define player collision boundaries
min_x = 50
max_x = window_w - 50
min_y = 100
max_y = window_h - 50

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
    elif stance == 3:
        glColor3f(0, 1, 1)  # Teal - Enemy stance
        return [0, 1, 1]

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
    global window_h, window_w
    glViewport(0, 0, window_w, window_h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, window_w, 0.0, window_h, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def display():
    global player_x, player_y, player_stance, enemy_x, enemy_y, enemy_stance
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 0)
    glLoadIdentity()
    iterate()

    # Draw player character
    stanceColor(player_stance)

    # Smaller player size (adjusted radius for head, arms, legs)
    head_radius = 7  # Smaller head radius
    mCircle(player_x, player_y, head_radius)

    # Body (Adjusted size)
    mLine(player_x, player_y - head_radius, player_x, player_y - 30)  # Center line
    
    # Arms
    mLine(player_x, player_y - 15, player_x - 10, player_y - 25)  # Left upper arm
    mLine(player_x - 10, player_y - 25, player_x - 15, player_y - 35)   
    mLine(player_x, player_y - 15, player_x + 10, player_y - 25)  # Right upper arm
    mLine(player_x + 10, player_y - 25, player_x + 15, player_y - 35)  
     
    # Legs
    mLine(player_x, player_y - 30, player_x - 7, player_y - 50)  # Left upper leg
    mLine(player_x - 7, player_y - 50, player_x - 10, player_y - 65)  
    mLine(player_x, player_y - 30, player_x + 7, player_y - 50)  # Right upper leg
    mLine(player_x + 7, player_y - 50, player_x + 10, player_y - 65)   

    # Hands and Feet
    mCircle(player_x - 15, player_y - 35, 2)  # Left hand
    mCircle(player_x + 15, player_y - 35, 2)  
    mCircle(player_x - 10, player_y - 65, 2)  # Left foot
    mCircle(player_x + 10, player_y - 65, 2)  

    # Sword
    mLine(player_x + 15, player_y - 35, player_x + 15, player_y - 25)  # Handle
    mLine(player_x + 15, player_y - 25, player_x + 20, player_y - 25)  # Cross guard
    mLine(player_x + 10, player_y - 25, player_x + 15, player_y - 25)
    mLine(player_x + 15, player_y - 25, player_x + 15, player_y)  # Blade
    mLine(player_x + 10, player_y - 25, player_x + 10, player_y)
    mLine(player_x + 20, player_y - 25, player_x + 20, player_y)
    mLine(player_x + 10, player_y, player_x + 15, player_y + 7)  # Tip
    mLine(player_x + 20, player_y, player_x + 15, player_y + 7)

    # Draw enemy (teal/off-white color)
    stanceColor(enemy_stance)
    mCircle(enemy_x, enemy_y, 10)  # Example enemy (a circle)

    glutSwapBuffers()

def check_collision(player_x, player_y, enemy_x, enemy_y):
    # Define the player hitbox (adjusted size for smaller player)
    player_left = player_x - 15  # Adjusted for smaller player
    player_right = player_x + 15
    player_top = player_y + 10
    player_bottom = player_y - 30
    
    # Check if the enemy is within the player's hitbox
    if (player_left < enemy_x < player_right) and (player_bottom < enemy_y < player_top):
        return True
    return False

def keyboardListener(key, x, y):
    global pause, player_stance, game_over, move_queue, m_count, player_x, player_y, enemy_x, enemy_y, enemy_stance
    
    if not pause and not game_over:
        # Stance changes for player only
        if key == b'q':
            player_stance = 1  # Green/Earth stance
        elif key == b'e':
            player_stance = 2  # Blue/Heaven stance
        elif key == b'r':
            player_stance = 0  # Red/Hell stance
            
        # Movement
        elif key == b'w':  # Up
            if player_y + move_speed <= max_y:   
                player_y += move_speed
        elif key == b's':  # Down
            if player_y - move_speed >= min_y:   
                player_y -= move_speed
        elif key == b'a':  # Left
            if player_x - move_speed >= min_x:  
                player_x -= move_speed
        elif key == b'd':  # Right
            if player_x + move_speed <= max_x:  # Check if within boundary
                player_x += move_speed
            
        # Check for collision when player is in blue stance
        if player_stance == 2:
            if check_collision(player_x, player_y, enemy_x, enemy_y):
                # Reset enemy position to a random new spot
                enemy_x = rdm.randint(50, window_w - 50)
                enemy_y = rdm.randint(50, window_h - 50)
                
    glutPostRedisplay()

# GLUT initialization
glutInit()
glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)
glutInitWindowSize(window_w, window_h)
glutCreateWindow(b"Test of Strength")
glutDisplayFunc(display)
glutKeyboardFunc(keyboardListener)
glutMainLoop()
