from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random as rdm #might not need this   

window_w, window_h = 720, 480
fps, t1, t2 = 60, 0, 0
player_stance = 0 #red is 0, green is 1, blue is 2, player starts 0 and on move becomes permanently 1 or 2
pause = False
move_queue = [None]*10 #only input is handled, movement is not implemented yet
m_count = 0
game_over = False

def stanceColor(stance):
    if stance==0:
        print('hell')
        return [1, 0, 0]
    elif stance==1:
        print('earth')
        return [0,1,0]
    elif stance==2:
        print('heaven')
        return [0,0,1]


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
        # print(x1_p,y1_p)
        # print('important', x2_p, y2_p)
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

def iterate():
    global window_h, window_w
    glViewport(0, 0, window_w, window_h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, window_w, 0.0, window_h, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def display():
    global window_h, window_w, player_stance
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0,0,0,0)
    glLoadIdentity()
    iterate()
    color_arr = stanceColor(player_stance)
    glColor3f(color_arr[0],color_arr[1],color_arr[2])
    mCircle(200,200,5)
    glutSwapBuffers()

def convert_coordinate(x,y):
    global window_w, window_h
    real_x = x - (window_w/2)
    real_y = (window_h/2) - y
    return real_x, real_y

def keyboardListener(key, x, y):
    global pause, player_stance, game_over, move_queue, m_count
    if pause==False:
        if game_over==False:
            if key==b'q':
                player_stance = 1 #green stance
            if key==b'e':
                player_stance = 2 #blue stance
            #moving left and right
            if key==b'a':
                move_queue[m_count] = False
                m_count += 1
                if m_count >= len(move_queue):
                    m_count = 0
                print(move_queue)
            if key==b'd': 
                move_queue[m_count] = True
                m_count +=1
                if m_count >= len(move_queue):
                    m_count = 0
                print(move_queue)
    glutPostRedisplay()


def init():
    glClearColor(0,0,0,0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104,	1,	1,	1000.0)


glutInit()
glutInitWindowSize(window_w,window_h)
glutInitWindowPosition(0,0)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA)

window = glutCreateWindow(b"Test of Strength")
init()

glutDisplayFunc(display)
glutKeyboardFunc(keyboardListener)

glutMainLoop()