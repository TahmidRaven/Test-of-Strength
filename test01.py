from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
# import numpy
import random as rdm

# Window and game state variables
difficulty = [0.5,1,2]
difficulty_select = 1 #these are multipliers for difficulty, when you choose easy normal hard, just direct ei multiplier will be chosen 
window_w, window_h = 720, 480
fps, t1, t2 = 60, 0, 0
player_stance, player_dir, player_state = 0, 0, 0  # red is 0, green is 1, blue is 2; dir left dir right = 1, 0; player state 0: walking, 1: jumping
player_attack_state = 0 #0 neutral, 1 attack, 2 block
pause = False
move_queue = [None]*10
jump_acceleration = 0
move_acceleration = 0
gravity, friction = 5, 5
m_count = 0
game_over = False



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

def iterate():
    global window_h, window_w
    glViewport(0, 0, window_w, window_h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, window_w, 0.0, window_h, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def display():
    global player_x, player_y, player_stance, t1, window_h, window_w, player_dir, ground, player_state
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 0)
    glLoadIdentity()
    iterate()
    t1 = glutGet(GLUT_ELAPSED_TIME)
    
    glColor3f(0.8,0.8,0.8)
    # Head
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
    # Right Sword
    if player_dir == 0:
        mLine(player_x+25, player_y-45, player_x+25, player_y-30)  # Handle
        mLine(player_x+25, player_y-30, player_x+30, player_y-30)  # Cross guard
        mLine(player_x+20, player_y-30, player_x+25, player_y-30)
        mLine(player_x+25, player_y-30, player_x+25, player_y)  # Blade
        mLine(player_x+20, player_y-30, player_x+20, player_y)
        mLine(player_x+30, player_y-30, player_x+30, player_y)
        mLine(player_x+20, player_y, player_x+25, player_y+10)  # Tip
        mLine(player_x+30, player_y, player_x+25, player_y+10)
    else:
        # Right Sword
        mLine(player_x-25, player_y-45, player_x-25, player_y-30)  # Handle
        mLine(player_x-25, player_y-30, player_x-30, player_y-30)  # Cross guard
        mLine(player_x-20, player_y-30, player_x-25, player_y-30)
        mLine(player_x-25, player_y-30, player_x-25, player_y)  # Blade
        mLine(player_x-20, player_y-30, player_x-20, player_y)
        mLine(player_x-30, player_y-30, player_x-30, player_y)
        mLine(player_x-20, player_y, player_x-25, player_y+10)  # Tip
        mLine(player_x-30, player_y, player_x-25, player_y+10)

    #sets state to regular if on ground

    # test
    mCircle(window_w/2, window_h/2, 20)
    collision(player_x-100, player_x+100, player_y-80, player_y+80, window_w/2-50, window_w/2+50, window_h/2-50, window_h/2+50)

    glutSwapBuffers()

def convert_coordinate(x,y):
    global window_w, window_h
    real_x = x - (window_w/2)
    real_y = (window_h/2) - y
    return real_x, real_y

def fps_animation():
    global move_queue, move_speed, player_x, player_y, t2, player_dir, jump_acceleration, gravity, ground, player_state, move_acceleration
    max = 20
    if (1000/fps-(t1-t2)<=0):
        for move in range(len(move_queue)):
            if move_queue[move] == False:
                move_acceleration -= move_speed
                move_queue[move] = None
                player_dir = 1
            elif move_queue[move] == True:
                move_acceleration += move_speed
                move_queue[move] = None
                player_dir = 0
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
            print(jump_acceleration)
        if player_y>ground:
            player_y-=gravity
        if player_y<ground:
            player_y = ground
        if player_y==ground:
            player_state = 0
            print('onground', player_state)
        
        t2=glutGet(GLUT_ELAPSED_TIME)
    


def animate():
    fps_animation()
    glutPostRedisplay()

def keyboardListener(key, x, y):
    global pause, player_stance, game_over, move_queue, m_count, player_x, player_y, m_count, jump_acceleration, player_state
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
                print('jumping', player_state)
            else:
                print('cant jump right now ')
        # elif key == b's':  # Down
        #     player_y -= move_speed
        if key==b'a':
            move_queue[m_count] = False
            m_count += 1
            if m_count >= len(move_queue):
                m_count = 0
        if key==b'd': 
            move_queue[m_count] = True
            m_count +=1
            if m_count >= len(move_queue):
                m_count = 0
            
        # Keep player within window bounds
        player_x = max(0, min(window_w, player_x))
        player_y = max(0, min(window_h, player_y))
    
    glutPostRedisplay()

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

glutMainLoop()