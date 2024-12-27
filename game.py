from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT.fonts import GLUT_BITMAP_TIMES_ROMAN_24,  GLUT_BITMAP_HELVETICA_18  
# import numpy
import random as rdm

# Window and game state variables
difficulty = [1,2,3]
difficulty_select = 1 #these are multipliers for difficulty, when you choose easy normal hard, just direct ei multiplier will be chosen 
window_w, window_h = 720, 480
fps, t1, t2 = 60, 0, 0
player_stance, player_dir, player_state = 1, 0, 0  # red is 0, green is 1, blue is 2; dir left dir right = 1, 0; player state 0: walking, 1: jumping
player_attack_state = 0 #0 neutral, 1 attack, 2 block
pause = False
move_queue = [None]*10
enemy_coords = []
jump_acceleration = 0
move_acceleration = 0
gravity, friction = 5, 5
m_count = 0
game_over = False
points = 0
hit_point = 5
boss_poise = 0
start_time, timer = 0, 0
enemy_max, enemy_count = 1, 0
knight_last_shot, witch_last_shot = 0, 0
boss_alive = False
projectiles = [] #x,y, color and direction
victory = False
game_over = False
last_hit = 0
last_boss_hit = 0
player_hit_flash, enemy_hit_flash, parry_flash = False, False, False

game_state = ["Title", "Level_1", "Level_2", "Level_3"]
current_state = game_state[0]

# Player position and movement
player_x = 360
player_y = 240
ground = 240
move_speed = 10

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

def losehp():
    global hit_point, last_hit, player_hit_flash
    current_time = glutGet(GLUT_ELAPSED_TIME)
    if current_time - last_hit >= 3000:
        hit_point -= 1
        last_hit = current_time
        player_hit_flash = True

def losepoise():
    global boss_poise, last_boss_hit, enemy_hit_flash
    current_time = glutGet(GLUT_ELAPSED_TIME)
    if current_time - last_boss_hit >= 2000:
        boss_poise -= 50
        last_boss_hit = current_time
        enemy_hit_flash = True



def findZone(dy, dx):
    if dy>=0 and dx>=0:
        if abs(dx)>=abs(dy):
            line_zone = 0
        else:
            line_zone = 1
    elif dy>=0 and dx<0:
        if abs(dx)>=abs(dy):
            line_zone = 3
        else:
            line_zone = 2
    elif dy<0 and dx<0:
        if abs(dx)>=abs(dy):
            line_zone = 4
        else:
            line_zone = 5
    elif dy<0 and dx>=0:
        if abs(dx)>=abs(dy):
            line_zone = 7
        else:
            line_zone = 6
    return line_zone

def converttoZone0(x,y,z):
    if z==0:
        return [x,y]
    elif z==1:
        return [y,x]
    elif z==2:
        return [y,-x]
    elif z==3:
        return [-x,y]
    elif z==4:
        return [-x,-y]
    elif z==5:
        return [-y,-x]
    elif z==6:
        return [-y,x]
    else:
        return [x,-y]

def converttoZone(x,y,z):
    if z==0:
        return [x,y]
    elif z==1:
        return [y,x]
    elif z==2:
        return [-y,x]
    elif z==3:
        return [-x,y]
    elif z==4:
        return [-x,-y]
    elif z==5:
        return [-y,-x]
    elif z==6:
        return [y,-x]
    else:
        return [x,-y]

def mLine(x1, y1, x2, y2):
    dy = y2-y1
    dx = x2-x1
    glBegin(GL_POINTS)
    glVertex2f(x1,y1)
    glEnd()

    zone = findZone(dy,dx)
    converted_coords = converttoZone0(x1, y1, zone)
    x1_p, y1_p = converted_coords[0], converted_coords[1]
    converted_coords = converttoZone0(x2, y2, zone)
    x2_p, y2_p = converted_coords[0], converted_coords[1]
    dy_p = y2_p-y1_p
    dx_p = x2_p-x1_p
    d = 2*dy_p-dx_p
    e_inc = 2*dy_p
    ne_inc = 2*dy_p-2*dx_p
    while x1_p!=x2_p:
        if d<=0:
            d+=e_inc
            x1_p+=1
        else:
            d+=ne_inc
            x1_p+=1
            y1_p+=1
        converted_coords = converttoZone(x1_p, y1_p, zone)
        x1, y1 = converted_coords[0], converted_coords[1]
        
        glBegin(GL_POINTS)
        glVertex2f(x1, y1)
        glEnd()

def mCircle(c_x, c_y, radius):
    d, x, y = 1-radius, 0, radius
    circlePoints(x,y,c_x,c_y)
    while x<y:
        if d<0:
            d+=2*x+3
            x+=1
        else:
            d+=2*x-2*y+5
            x+=1
            y-=1
        circlePoints(x,y,c_x,c_y)


def mTriangle(x1, y1, x2, y2, x3, y3):
  
    mLine(x1, y1, x2, y2)
    mLine(x2, y2, x3, y3)
    mLine(x3, y3, x1, y1)
    
    # min_x = min(x1, x2, x3)
    # max_x = max(x1, x2, x3)
    # min_y = min(y1, y2, y3)
    # max_y = max(y1, y2, y3)
    
    # # Scan each row
    # for y in range(int(min_y), int(max_y) + 1):
    #     for x in range(int(min_x), int(max_x) + 1):
       
    #         d1 = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
    #         d2 = (x3 - x2) * (y - y2) - (y3 - y2) * (x - x2)
    #         d3 = (x1 - x3) * (y - y3) - (y1 - y3) * (x - x3)
            
    #         has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    #         has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            
    #         if not (has_neg and has_pos):
    #             glBegin(GL_POINTS)
    #             glVertex2f(x, y)
    #             glEnd()

def circlePoints(x,y,cx,cy):
    glBegin(GL_POINTS)
    glVertex2f(x+cx,y+cy)
    glVertex2f(y+cx,x+cy)
    glVertex2f(y+cx,-x+cy)
    glVertex2f(x+cx,-y+cy)
    glVertex2f(-x+cx,-y+cy)
    glVertex2f(-y+cx,-x+cy)
    glVertex2f(-y+cx,x+cy)
    glVertex2f(-x+cx,y+cy)
    glEnd()

def collision(x1_l, x1_r, y1_d, y1_u, x2_l, x2_r, y2_d, y2_u):
    #this might not work, be careful
    if x1_l<=x2_r and x1_r>=x2_l:
        if y1_d<=y2_u and y1_u>=y2_d:
            return True #collision
    return False

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

def draw_goblin(x, y):
 
    glColor3f(0.8, 0.2, 0.2)  # Bright red 
    
    # Head 
    head_radius = 5  
    mCircle(x, y, head_radius)
    # Body  
    mLine(x, y - head_radius, x, y - 20)  # Main body
     # Arms  
    mLine(x, y - 10, x - 8, y - 18)  # Left arm
    mLine(x, y - 10, x + 8, y - 18)  
    
    # Little claws 
    mCircle(x - 8, y - 18, 2)  # Left hand
    mCircle(x + 8, y - 18, 2)   
    # Legs 
    mLine(x, y - 20, x - 5, y - 35)  # Left leg
    mLine(x, y - 20, x + 5, y - 35)  
   # Feet
    mCircle(x - 5, y - 35, 2)  # Left foot
    mCircle(x + 5, y - 35, 2)   
   # pointy ears 
    mTriangle(x - 5, y, x - 8, y + 5, x - 2, y + 2)  # Left ear
    mTriangle(x + 5, y, x + 8, y + 5, x + 2, y + 2)

def knight_shoot():
    global knight_last_shot, projectiles, boss_alive, enemy_coords, player_x
    current_time = glutGet(GLUT_ELAPSED_TIME)
    #x,y, color and direction 1 = right, 0 = left
    if current_time - knight_last_shot >= 4000 and boss_alive:
        if enemy_coords[0][0]>player_x:
            projectiles.append([enemy_coords[0][0], enemy_coords[0][1], rdm.randint(0,2), 0])
        else:
            projectiles.append([enemy_coords[0][0], enemy_coords[0][1], rdm.randint(0,2), 1])
        knight_last_shot = current_time

def witch_shoot(witch):
    global witch_last_shot, projectiles, player_x, boss_alive
    current_time = glutGet(GLUT_ELAPSED_TIME)
    #x,y, color and direction 1 = right, 0 = left
    if boss_alive == False:
        if current_time - witch_last_shot >= 4000:
            if witch[0]>player_x:
                projectiles.append([witch[0], witch[1], rdm.randint(0,2), 0])
            else:
                projectiles.append([witch[0], witch[1], rdm.randint(0,2), 1])
            witch_last_shot = current_time
    else:
        if current_time - witch_last_shot >= 3000:
            if witch[0]>player_x:
                projectiles.append([witch[0], witch[1], rdm.randint(0,2), 0])
            else:
                projectiles.append([witch[0], witch[1], rdm.randint(0,2), 1])
            witch_last_shot = current_time

def goblin_move(goblin):
    global player_x, boss_alive
    if boss_alive==False:
        if goblin[0]>player_x:
            goblin[0] -= 1
        else:
            goblin[0] += 1
    else:
        if goblin[0]>player_x:
            goblin[0] -= 3
        else:
            goblin[0] += 3

def iterate():
    global window_h, window_w
    glViewport(0, 0, window_w, window_h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, window_w, 0.0, window_h, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def display():
    #unfortunately, everything is displayed here
    global player_x, player_y, player_stance, t1, window_h, window_w, player_dir, ground, player_state, player_attack_state, points, hit_point, current_state, timer, boss_poise, player_hit_flash, parry_flash, enemy_hit_flash
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if player_hit_flash:
        glClearColor(0.2, 0, 0, 0)
        player_hit_flash = False
    elif parry_flash:
        if player_stance == 1:
            glClearColor(0, 0.2, 0, 0)
        else:
            glClearColor(0, 0, 0.2, 0)
        parry_flash = False
    elif enemy_hit_flash:
        glClearColor(0.2,0.2,0.2,0)
        enemy_hit_flash = False
    else:
        glClearColor(0, 0, 0, 0)
    glLoadIdentity()
    iterate()
    t1 = glutGet(GLUT_ELAPSED_TIME)
    timer = glutGet(GLUT_ELAPSED_TIME)
    
 
    
    if current_state!="Title":
        glColor3f(0.5,0.5,0.5)
        glRasterPos2f(50,window_h-50)
        point = f"Points: {points}"
        hp = f"Health: {hit_point}"
        for letter in point:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(letter))
        glRasterPos2f(200,window_h-50)
        for letter in hp:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(letter))
        if boss_poise!=0:
            glRasterPos2f(window_w-200,window_h-50)
            poise = f"Poise: {boss_poise}"
            for letter in poise:
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(letter))

        # Head
        glColor3f(0.8,0.8,0.8)
        mCircle(player_x, player_y, 10)

        # Body
        mLine(player_x, player_y-10, player_x, player_y-40)  # Center line
        
        # Arms
        mLine(player_x, player_y-20, player_x-15, player_y-30)  # Left upper arm
        mLine(player_x-15, player_y-30, player_x-25, player_y-45)   
        mLine(player_x, player_y-20, player_x+15, player_y-30)  # Right upper arm
        mLine(player_x+15, player_y-30, player_x+25, player_y-45)  
        
        # Legs
        mLine(player_x, player_y-40, player_x-10, player_y-60)  # Left upper leg
        mLine(player_x-10, player_y-60, player_x-15, player_y-80)  
        mLine(player_x, player_y-40, player_x+10, player_y-60)  # Right upper leg
        mLine(player_x+10, player_y-60, player_x+15, player_y-80)   

        # Hands and Feet
        mCircle(player_x-25, player_y-45, 3)  # Left hand
        mCircle(player_x+25, player_y-45, 3)  
        mCircle(player_x-15, player_y-80, 3)  # Left foot
        mCircle(player_x+15, player_y-80, 3)  

        stanceColor(player_stance)
        #0 neutral, 1 attack, 2 block
        # Right Sword
        if player_dir == 0:
            if player_attack_state == 2:
                mLine(player_x+25, player_y-45, player_x+25, player_y-30)  # Handle
                mLine(player_x+25, player_y-30, player_x+30, player_y-30)  # Cross guard
                mLine(player_x+20, player_y-30, player_x+25, player_y-30)
                mLine(player_x+25, player_y-30, player_x+25, player_y)  # Blade
                mLine(player_x+20, player_y-30, player_x+20, player_y)
                mLine(player_x+30, player_y-30, player_x+30, player_y)
                mLine(player_x+20, player_y, player_x+25, player_y+10)  # Tip
                mLine(player_x+30, player_y, player_x+25, player_y+10)
            elif player_attack_state == 1:
                mLine(player_x+25, player_y-45, player_x+40, player_y-45)  # Handle
                mLine(player_x+40, player_y-40, player_x+40, player_y-45)  # Cross guard
                mLine(player_x+40, player_y-45, player_x+40, player_y-50)
                mLine(player_x+40, player_y-45, player_x+70, player_y-45)  # Blade
                mLine(player_x+40, player_y-40, player_x+70, player_y-40)
                mLine(player_x+40, player_y-50, player_x+70, player_y-50)
                mLine(player_x+70, player_y-40, player_x+80, player_y-45)  # Tip
                mLine(player_x+70, player_y-50, player_x+80, player_y-45)
            elif player_attack_state == 0:
                mLine(player_x+25, player_y-45, player_x+30, player_y-30)  # Handle
                mLine(player_x+25, player_y-25, player_x+30, player_y-30)  # Cross guard
                mLine(player_x+30, player_y-30, player_x+35, player_y-35)
                mLine(player_x+25, player_y-25, player_x+35, player_y)
                mLine(player_x+30, player_y-30, player_x+42, player_y)  # Blade
                mLine(player_x+35, player_y-35, player_x+48, player_y-5)
                mLine(player_x+35, player_y, player_x+43, player_y+10)  # Tip
                mLine(player_x+43, player_y+10, player_x+48, player_y-7)
        else:
            if player_attack_state == 2:
            # Left Sword
                mLine(player_x-25, player_y-45, player_x-25, player_y-30)  # Handle
                mLine(player_x-25, player_y-30, player_x-30, player_y-30)  # Cross guard
                mLine(player_x-20, player_y-30, player_x-25, player_y-30)
                mLine(player_x-25, player_y-30, player_x-25, player_y)  # Blade
                mLine(player_x-20, player_y-30, player_x-20, player_y)
                mLine(player_x-30, player_y-30, player_x-30, player_y)
                mLine(player_x-20, player_y, player_x-25, player_y+10)  # Tip
                mLine(player_x-30, player_y, player_x-25, player_y+10)
            elif player_attack_state == 1:
                mLine(player_x-25, player_y-45, player_x-40, player_y-45)  # Handle
                mLine(player_x-40, player_y-40, player_x-40, player_y-45)  # Cross guard
                mLine(player_x-40, player_y-45, player_x-40, player_y-50)
                mLine(player_x-40, player_y-45, player_x-70, player_y-45)  # Blade
                mLine(player_x-40, player_y-40, player_x-70, player_y-40)
                mLine(player_x-40, player_y-50, player_x-70, player_y-50)
                mLine(player_x-70, player_y-40, player_x-80, player_y-45)  # Tip
                mLine(player_x-70, player_y-50, player_x-80, player_y-45)
            elif player_attack_state == 0:
                mLine(player_x-25, player_y-45, player_x-30, player_y-30)  # Handle
                mLine(player_x-25, player_y-25, player_x-30, player_y-30)  # Cross guard
                mLine(player_x-30, player_y-30, player_x-35, player_y-35)
                mLine(player_x-25, player_y-25, player_x-35, player_y)
                mLine(player_x-30, player_y-30, player_x-42, player_y)  # Blade
                mLine(player_x-35, player_y-35, player_x-48, player_y-5)
                mLine(player_x-35, player_y, player_x-43, player_y+10)  # Tip
                mLine(player_x-43, player_y+10, player_x-48, player_y-7)


    else:
        glColor3f(0.5,0.5,0.5)
        glRasterPos2f(window_w/2-80,window_h-50)
        title = "Test of Strength"
        difficulty, start, end = "Difficulty", "Start", "Exit"
        easy, normal, hard = "Easy", "Normal", "Hard"
        for letter in title:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(letter))
        glRasterPos2f(window_w/2-80,200)
        for letter in difficulty:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(letter))
        glRasterPos2f(window_w/2-100,150)
        for letter in easy:
            glutBitmapCharacter( GLUT_BITMAP_HELVETICA_18 , ord(letter))
        glRasterPos2f(window_w/2,150)
        for letter in normal:
            glutBitmapCharacter( GLUT_BITMAP_HELVETICA_18 , ord(letter))
        glRasterPos2f(window_w/2+100,150)
        for letter in hard:
            glutBitmapCharacter( GLUT_BITMAP_HELVETICA_18 , ord(letter))
        glRasterPos2f(window_w/2-80,300)
        for letter in start:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(letter))   
        glRasterPos2f(window_w/2-80,100)
        for letter in end:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(letter))   



    #sets state to regular if on ground

    # test
    enemy_spawner()
    enemy_drawer()
    enemy_collision()
    projectile_drawer()

    glutSwapBuffers()

def projectile_drawer():
    global projectiles
    for projectile in projectiles:
        if projectile!=None:
            #x,y, color and direction 1 = right, 0 = left
            stanceColor(projectile[2])
            mCircle(projectile[0], projectile[1], 5)

def enemy_spawner():
    global start_time, timer, current_state, enemy_coords, ground, enemy_max, enemy_count, boss_alive, difficulty, difficulty_select, boss_poise, player_x, player_y
    if (timer-start_time)%10 == 0:
        if enemy_count<enemy_max+difficulty[difficulty_select]:
            if current_state=='Level_3':
                if points<1000:
                # enemy_coords.append([rdm.randint(20, window_w-20), ground-100, rdm.randint(0,2)]) final code
                    spawn_coords = [rdm.randint(player_x-400, player_x+400), ground-40]
                    if spawn_coords[0]>window_w:
                        spawn_coords[0] = window_w
                    elif spawn_coords[0]<0:
                        spawn_coords[0] = 0
                    enemy_coords.append([spawn_coords[0], spawn_coords[1], rdm.randint(0,1)]) #test code
                    enemy_count += 1
                else:
                    if boss_alive==False:
                        spawn_coords = [rdm.randint(player_x-400, player_x+400), ground-20]
                        if spawn_coords[0]>window_w:
                            spawn_coords[0] = window_w
                        elif spawn_coords[0]<0:
                            spawn_coords[0] = 0
                        enemy_coords = [[spawn_coords[0], spawn_coords[1], 2]]
                        boss_alive = True
                        boss_poise = 500*difficulty[difficulty_select]

def enemy_drawer():
    global enemy_coords, current_state
    if boss_alive==True:
        if current_state == 'Level_3':
            draw_knight_boss(enemy_coords[0][0],enemy_coords[0][1])
    else:
        for coord in enemy_coords:
            if coord!=None:
                if coord[2] == 1:
                    draw_witch(coord[0], coord[1])
                elif coord[2] == 0:
                    draw_goblin(coord[0], coord[1])


def enemy_collision():
    global enemy_coords, player_attack_state, player_x, player_y, points, player_dir,enemy_count,boss_alive, boss_poise, current_state, projectiles, player_stance, hit_point, parry_flash, enemy_hit_flash
    if player_attack_state == 1:
        if boss_alive==False:
            for coord in range(len(enemy_coords)):
                if enemy_coords[coord]!=None:
                    if collision(player_x-10, player_x+10, player_y-50, player_y+50, enemy_coords[coord][0], enemy_coords[coord][0], enemy_coords[coord][1], enemy_coords[coord][1]):
                        losehp()
                    if player_dir == 0:
                        if collision(player_x+25, player_x+80, player_y-50, player_y-40, enemy_coords[coord][0], enemy_coords[coord][0], enemy_coords[coord][1], enemy_coords[coord][1]):
                            enemy_coords[coord] = None
                            points += 100
                            enemy_count-=1
                            enemy_hit_flash = True
                    else:
                        if collision(player_x-80, player_x-25, player_y-50, player_y-40, enemy_coords[coord][0], enemy_coords[coord][0], enemy_coords[coord][1], enemy_coords[coord][1]):
                            enemy_coords[coord] = None
                            points += 100
                            enemy_count-=1
                            enemy_hit_flash = True
        else:
            # print(player_x+25, player_x+80, player_y-50, player_y-40, enemy_coords[0][0], enemy_coords[0][0], enemy_coords[0][1], enemy_coords[0][1])
            if collision(player_x-10, player_x+10, player_y-50, player_y+50, enemy_coords[0][0], enemy_coords[0][0], enemy_coords[0][1], enemy_coords[0][1]):
                losehp()
            if player_dir == 0:
                if collision(player_x+25, player_x+80, player_y-50, player_y-40, enemy_coords[0][0]-20, enemy_coords[0][0]+20, enemy_coords[0][1]-100, enemy_coords[0][1]+200):
                    if boss_poise>0:
                        losepoise()
                    else:
                        enemy_hit_flash = True
                        enemy_coords[0] = None
                        boss_alive = False
                        current_state = "Title"
            else:
                if collision(player_x-80, player_x-25, player_y-50, player_y-40, enemy_coords[0][0]-20, enemy_coords[0][0]+20, enemy_coords[0][1]-100, enemy_coords[0][1]+200):
                    # print('??')
                    if boss_poise>0:
                        losepoise()
                    else:
                        enemy_hit_flash = True
                        enemy_coords[0] = None
                        boss_alive = False
                        print('You win!')
                        current_state = "Title"
    if player_attack_state == 2:
        for coord in range(len(enemy_coords)):
            if enemy_coords[coord]!=None:
                if collision(player_x+10, player_x-10, player_y-50, player_y+50, enemy_coords[coord][0], enemy_coords[coord][0], enemy_coords[coord][1], enemy_coords[coord][1]):
                    losehp()
        for coord in range(len(projectiles)):
            if projectiles[coord]!=None:
                if player_dir == 0:
                    if collision(player_x+25, player_x+50, player_y-100, player_y+100, projectiles[coord][0], projectiles[coord][0], projectiles[coord][1], projectiles[coord][1]):
                        if player_stance==projectiles[coord][2]:
                            projectiles[coord] = None
                            points += 100
                            hit_point+=1
                            parry_flash = True
                        else:
                            losehp()
                else:
                    if collision(player_x-50, player_x-25, player_y-100, player_y+100, projectiles[coord][0], projectiles[coord][0], projectiles[coord][1], projectiles[coord][1]):
                        if player_stance==projectiles[coord][2]:
                            projectiles[coord] = None
                            points += 100
                            hit_point+=1
                            parry_flash = True
                        else:
                            losehp()
    if player_attack_state == 0:
        for coord in range(len(enemy_coords)):
            if enemy_coords[coord]!=None:
                if collision(player_x-10, player_x+10, player_y-50, player_y+50, enemy_coords[coord][0], enemy_coords[coord][0], enemy_coords[coord][1], enemy_coords[coord][1]):
                    losehp()
        for coord in range(len(projectiles)):
            if projectiles[coord]!=None:
                # print(player_x+10, player_x-10, player_y-50, player_y+50, projectiles[coord][0], projectiles[coord][0], projectiles[coord][1], enemy_coords[coord][1])
                if player_dir == 0:
                    if collision(player_x-10, player_x+10, player_y-50, player_y+50, projectiles[coord][0], projectiles[coord][0], projectiles[coord][1], projectiles[coord][1]):
                            losehp()
                else:
                    if collision(player_x-10, player_x+10, player_y-50, player_y+50, projectiles[coord][0], projectiles[coord][0], projectiles[coord][1], projectiles[coord][1]):
                            losehp()
    if hit_point<=0:
        print('Game Over')
        glutLeaveMainLoop()


            

def projectile_animation():
    global projectiles, window_w
    for projectile in range(len(projectiles)):
        if projectiles[projectile]!=None:
            #x,y, color and direction 1 = right, 0 = left
            if projectiles[projectile][3]==1:
                projectiles[projectile][0] += 10
            else:
                projectiles[projectile][0] -= 10
            if projectiles[projectile][0] > window_w or projectiles[projectile][0]<0:
                projectiles[projectile] = None
                


def fps_animation():
    global move_queue, move_speed, player_x, player_y, t2, player_dir, jump_acceleration, gravity, ground, player_state, move_acceleration, enemy_coords, boss_alive
    max = 20
    if (1000/fps-(t1-t2)<=0):
        for move in range(len(move_queue)):
            if move_queue[move] == 0:
                move_acceleration -= move_speed
                move_queue[move] = None
                player_dir = 1
            elif move_queue[move] == 1:
                move_acceleration += move_speed
                move_queue[move] = None
                player_dir = 0
            elif move_queue[move] == 2:
                if player_dir == 1:
                    player_x -= 200
                    move_queue[move] = None
                else:
                    player_x += 200
                    move_queue[move] = None
        projectile_animation()
        if boss_alive==False:
            for enemy in enemy_coords:
                if enemy!=None: #0 is goblin, 1 is witch x y type
                    if enemy[2] == 0:
                        goblin_move(enemy)
                    elif enemy[2] == 1:
                        witch_shoot(enemy)
        else:
            if enemy_coords[0]!=None:
                if rdm.randint(0,1)==0:
                    goblin_move(enemy_coords[0])
                else:
                    witch_shoot(enemy_coords[0])
        if move_acceleration>max:
            move_acceleration = max
        if move_acceleration<-max:
            move_acceleration = -max
        player_x += move_acceleration
        if move_acceleration>0:
            move_acceleration -= friction
        elif move_acceleration<0:
            move_acceleration += friction
        player_y+=jump_acceleration
        if jump_acceleration>=0:
            jump_acceleration-=gravity
        if player_y>ground:
            player_y-=gravity
        if player_y<ground:
            player_y = ground
        if player_y==ground:
            player_state = 0
        
        t2=glutGet(GLUT_ELAPSED_TIME)

    


def animate():
    fps_animation()
    glutPostRedisplay()

def keyboardListener(key, x, y):
    global pause, player_stance, game_over, move_queue, m_count, player_x, player_y, m_count, jump_acceleration, player_state, player_attack_state
    #player state 0: walking, 1: jumping
    if not pause and not game_over:
        # Stance changes
        if key == b'q':
            player_stance = 1  # Green/Earth stance
        elif key == b'e':
            player_stance = 2  # Blue/Heaven stance
        elif key == b'r':
            player_stance = 0  # Red/Hell stance
            
        # Movement
        elif key == b' ':
            if player_state==0:
                player_state = 1  # Up
                jump_acceleration += 50
            else:
                print('cant jump right now ')
        # elif key == b's':  # Down
        #     player_y -= move_speed
        if player_attack_state == 0:
            if key==b'a':
                move_queue[m_count] = 0
                m_count += 1
                if m_count >= len(move_queue):
                    m_count = 0
            if key==b'd': 
                move_queue[m_count] = 1
                m_count +=1
                if m_count >= len(move_queue):
                    m_count = 0
        if key==b's':
            move_queue[m_count] = 2
            m_count +=1
            if m_count >= len(move_queue):
                m_count = 0
            
        # Keep player within window bounds
        player_x = max(0, min(window_w, player_x))
        player_y = max(0, min(window_h, player_y))
    
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global player_attack_state, current_state, window_w, window_h, game_state, difficulty_select, start_time
    if current_state!="Title":
        if button==GLUT_LEFT_BUTTON:
            if state==GLUT_DOWN:
                player_attack_state = 1
            if state==GLUT_UP:
                player_attack_state = 0
        if button==GLUT_RIGHT_BUTTON:
            if state==GLUT_DOWN:
                player_attack_state = 2
            if state==GLUT_UP:
                player_attack_state = 0
    else:
        if button==GLUT_LEFT_BUTTON:
            if state==GLUT_DOWN:
                start_time = glutGet(GLUT_ELAPSED_TIME)
                # print(x,x,y,y)
                if collision(x,x,y,y,window_w/2-80, window_w/2, 150, 200): #start game game_state = ["Title", "Level_1", "Level_2", "Level_3"]
                    # current_state=game_state[1]
                    current_state = game_state[3]
                if collision(x,x,y,y,230, 300, 300, 340): #easy
                    difficulty_select=0
                    print('easy')
                if collision(x,x,y,y,350, 400, 300, 340): #normal
                    difficulty_select=1
                    print('normal')
                if collision(x,x,y,y,450, 500, 300, 340): #hard
                    difficulty_select=2
                    print('hard')
                if collision(x,x,y,y,250, 350, 360, 390):
                    glutLeaveMainLoop()

                
        if button==GLUT_RIGHT_BUTTON:
            if state==GLUT_DOWN:
                player_attack_state = 2
            if state==GLUT_UP:
                player_attack_state = 0


def init():
    glClearColor(0,0,0,0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, 1, 1, 1000.0)

# Initialize and run the game
glutInit()
glutInitWindowSize(window_w, window_h)
glutInitWindowPosition(0, 0)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA)

window = glutCreateWindow(b"Test of Strength")
init()

glutDisplayFunc(display)
glutIdleFunc(animate)
glutKeyboardFunc(keyboardListener)
glutMouseFunc(mouseListener)

glutMainLoop()