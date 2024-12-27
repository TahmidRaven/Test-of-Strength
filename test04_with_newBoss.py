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

game_won = False

# Player position and movement
player_x = 360
player_y = 240
move_speed = 8

# Witch position and state
witch_x, witch_y = 100, 100
witch_alive = True

# Knight boss position and state
knight_x, knight_y = 500, 100
knight_alive = False
knight_hp = 3
knight_last_shot = 0
knight_shoot_delay = 1.5
knight_projectiles = []
knight_move_timer = 0
knight_move_delay = 3

# Projectiles
class Projectile:
    def __init__(self, x, y, dx, dy, speed=3):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.radius = 5

class KnightProjectile(Projectile):
    def __init__(self, x, y, dx, dy):
        super().__init__(x, y, dx, dy, speed=4)
        self.radius = 7

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
    glColor3f(0.5, 0, 0.5)
    mTriangle(x, y + 30, x - 15, y + 10, x + 15, y + 10)
    mLine(x - 20, y + 10, x + 20, y + 10)
    mCircle(x, y, 10)
    mTriangle(x, y - 10, x - 20, y - 40, x + 20, y - 40)
    mLine(x - 15, y - 20, x - 25, y - 10)
    mLine(x + 15, y - 20, x + 25, y - 10)

def draw_knight_boss(x, y):
    head_radius = 12
    glColor3f(0.7, 0.7, 0.7)
    mCircle(x, y, head_radius)
    mLine(x - head_radius, y, x + head_radius, y)
    mLine(x, y + head_radius, x, y + head_radius + 5)
    mLine(x - 20, y - head_radius, x + 20, y - head_radius)
    mLine(x - 20, y - head_radius, x - 25, y - 45)
    mLine(x + 20, y - head_radius, x + 25, y - 45)
    mLine(x - 25, y - 45, x + 25, y - 45)
    mCircle(x - 20, y - head_radius - 5, 8)
    mCircle(x + 20, y - head_radius - 5, 8)
    mLine(x - 20, y - 25, x - 30, y - 40)
    mLine(x - 21, y - 25, x - 31, y - 40)
    mLine(x + 20, y - 25, x + 35, y - 35)
    mLine(x + 21, y - 25, x + 36, y - 35)
    mLine(x - 15, y - 45, x - 20, y - 70)
    mLine(x - 14, y - 45, x - 19, y - 70)
    mCircle(x - 20, y - 70, 5)
    mLine(x + 15, y - 45, x + 20, y - 70)
    mLine(x + 14, y - 45, x + 19, y - 70)
    mCircle(x + 20, y - 70, 5)
    mTriangle(x - 30, y - 40, x - 40, y - 35, x - 35, y - 55)
    mLine(x - 35, y - 40, x - 35, y - 50)
    mLine(x - 33, y - 45, x - 37, y - 45)
    mLine(x + 35, y - 35, x + 35, y - 25)
    mLine(x + 30, y - 25, x + 40, y - 25)
    mLine(x + 35, y - 25, x + 35, y + 5)
    mLine(x + 33, y - 25, x + 33, y + 3)
    mLine(x + 37, y - 25, x + 37, y + 3)
    mTriangle(x + 33, y + 3, x + 37, y + 3, x + 35, y + 8)

def check_sword_collision():
    global witch_alive, knight_alive, knight_hp, game_won
    
    sword_tip_x = player_x + 15
    sword_tip_y = player_y + 7
    sword_base_x = player_x + 15
    sword_base_y = player_y - 25
    
    if witch_alive:
        distance_tip = math.sqrt((sword_tip_x - witch_x)**2 + (sword_tip_y - witch_y)**2)
        distance_base = math.sqrt((sword_base_x - witch_x)**2 + (sword_base_y - witch_y)**2)
        if distance_tip < 20 or distance_base < 20:
            witch_alive = False
            knight_alive = True
            return True
            
    elif knight_alive:
        distance_tip = math.sqrt((sword_tip_x - knight_x)**2 + (sword_tip_y - knight_y)**2)
        distance_base = math.sqrt((sword_base_x - knight_x)**2 + (sword_base_y - knight_y)**2)
        if distance_tip < 20 or distance_base < 20:
            knight_hp -= 1
            if knight_hp <= 0:
                knight_alive = False
                game_won = True  #  game_won == knight is defeated
            return True
    return False

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
        projectiles.append(Projectile(witch_x, witch_y, dx, dy))
        last_shot_time = current_time

def knight_shoot():
    global knight_last_shot
    current_time = time.time()
    
    if current_time - knight_last_shot >= knight_shoot_delay and knight_alive:
        dx = player_x - knight_x
        dy = player_y - knight_y
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            dx /= length
            dy /= length
        
        knight_projectiles.append(KnightProjectile(knight_x, knight_y, dx, dy))
        knight_projectiles.append(KnightProjectile(knight_x, knight_y, dx * 0.866 - dy * 0.5, dy * 0.866 + dx * 0.5))
        knight_projectiles.append(KnightProjectile(knight_x, knight_y, dx * 0.866 + dy * 0.5, dy * 0.866 - dx * 0.5))
        knight_last_shot = current_time

def update_knight():
    global knight_x, knight_y, knight_move_timer
    current_time = time.time()
    
    if current_time - knight_move_timer >= knight_move_delay:
        # Move towards player
        dx = player_x - knight_x
        dy = player_y - knight_y
        length = math.sqrt(dx**2 + dy**2)
        if length > 150:  # Keep some distance
            if length > 0:
                knight_x += (dx/length) * 30
                knight_y += (dy/length) * 30
        knight_move_timer = current_time

# Modify update_projectiles()
def update_projectiles():
    global game_over
    # Update normal projectiles
    for proj in projectiles[:]:
        proj.x += proj.dx * proj.speed
        proj.y += proj.dy * proj.speed
        if (proj.x < 0 or proj.x > window_w or 
            proj.y < 0 or proj.y > window_h):
            projectiles.remove(proj)
            continue
        distance = math.sqrt((proj.x - player_x)**2 + (proj.y - player_y)**2)
        if distance < 20:
            game_over = True
            
    # Update knight projectiles
    for proj in knight_projectiles[:]:
        proj.x += proj.dx * proj.speed
        proj.y += proj.dy * proj.speed
        if (proj.x < 0 or proj.x > window_w or 
            proj.y < 0 or proj.y > window_h):
            knight_projectiles.remove(proj)
            continue
        distance = math.sqrt((proj.x - player_x)**2 + (proj.y - player_y)**2)
        if distance < 20:
            game_over = True

# Modify reset_game()
def reset_game():
    global player_x, player_y, witch_x, witch_y, witch_alive, game_over, projectiles, player_stance
    global knight_x, knight_y, knight_alive, knight_hp, knight_projectiles, knight_last_shot, knight_move_timer
    global game_won
    
    player_x = 360
    player_y = 240
    witch_x = 100
    witch_y = 100
    witch_alive = True
    knight_x = 500
    knight_y = 100
    knight_alive = False
    knight_hp = 3
    projectiles.clear()
    knight_projectiles.clear()
    knight_last_shot = 0
    knight_move_timer = 0
    game_over = False
    game_won = False
    player_stance = 0

# Modify update() function
def update(value):
    if not pause and not game_over:
        witch_shoot()
        if knight_alive:
            knight_shoot()
            update_knight()
        update_projectiles()
        check_sword_collision()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

# Modify display() to draw knight projectiles
def display():
    global player_x, player_y, player_stance, witch_x, witch_y
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 0)
    glLoadIdentity()
    iterate()
 
    if not game_over and not game_won:
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

        # Draw witch if alive
        if witch_alive:
            draw_witch(witch_x, witch_y)
            
        # Draw knight boss if alive
        if knight_alive:
            draw_knight_boss(knight_x, knight_y)
     
        # Draw projectiles
        glColor3f(1, 0, 1)   
        for proj in projectiles:
            mCircle(int(proj.x), int(proj.y), proj.radius)   
        
        # Draw knight projectiles
        glColor3f(0.7, 0.7, 0.7)
        for proj in knight_projectiles:
            mCircle(int(proj.x), int(proj.y), proj.radius)
        
    if game_over:
        glColor3f(1, 0, 0)
 
        glRasterPos2f(window_w//2 - 40, window_h//2)
        for c in "You DIED lonely Knight":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
 
        glRasterPos2f(window_w//2 - 90, window_h//2 - 30)
        for c in "Press SPACE to restart":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(c))
            
    if game_won:
        glColor3f(0, 1, 0)  # Green color for victory
 
        glRasterPos2f(window_w//2 - 60, window_h//2)
        for c in "VICTORY ACHIEVED MY LOYAL KNIGHT!!!":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
 
        glRasterPos2f(window_w//2 - 90, window_h//2 - 30)
        for c in "Press SPACE to play again":
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