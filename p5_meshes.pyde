# Provided code for Subdivison and Geodesic Spheres
# sliu749@gatech.edu

from __future__ import division
import traceback
import random

# parameters used for object rotation by mouse
mouseX_old = 0
mouseY_old = 0
rot_mat = PMatrix3D()
vertices = []
faces = []
faces_color = None
opposite_corner = []
current_corner = 0
show_corner = True
corner_mat = None

def resetFaceColor():
    global faces_color
    faces_color = []
    for f in faces:
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        faces_color.append(color(r,g,b))

def cornerFace(corner):
    return int(corner/3)

def cornerVertexIndex(corner):
    face = cornerFace(corner)
    index = corner - face * 3
    return faces[face][index]
 
def cornerVertex(corner):
    return vertices[cornerVertexIndex(corner)] 

def nextCorner(corner):
    face = cornerFace(corner)
    return face * 3 + (corner + 1) % 3

def prevCorner(corner):
    return nextCorner(nextCorner(corner))
    
def resetCornerMatrix():
    p0 = cornerVertex(current_corner)
    p1 = cornerVertex(nextCorner(current_corner))
    p2 = cornerVertex(prevCorner(current_corner))
    v1 = p1 - p0
    v1.normalize()
    v2 = p2 - p0
    v2.normalize()
    v = v1 + v2
    v.normalize()

    alpha = acos(v1.dot(v))
    sinA = sin(alpha)
    r = 0.06
    center_dist = r * 1.2 / sinA
    
    a = p1.dist(p0)
    b = p2.dist(p0)
    c = p2.dist(p1)


    #50% of the distance from p0 to the center of the inscribed circle
    max_center_dist = 0.5 * (a * b * sin(alpha*2) / ((a + b + c) * sinA))
     
    if center_dist > max_center_dist:
        center_dist = max_center_dist
        r = center_dist * sinA / 1.2
        
    v.mult(center_dist)
    p = p0 + v;

    global corner_mat
    corner_mat = PMatrix3D()
    corner_mat.translate(p.x,p.y,p.z)
    corner_mat.scale(r)

def resetOppositeCorner():    
    n = len(faces) * 3
    global opposite_corner
    opposite_corner = [-1] * n
    for a in range(n):
        an = cornerVertexIndex(nextCorner(a))
        ap = cornerVertexIndex(prevCorner(a))
        for b in range(n):
            if an == cornerVertexIndex(prevCorner(b)) and ap == cornerVertexIndex(nextCorner(b)):
                opposite_corner[a] = b
                opposite_corner[b] = a
                
def inflate():
    for p in vertices:
        p.normalize()
    resetCornerMatrix()
    
def onMeshChanged():
    resetOppositeCorner()
    resetCornerMatrix()
    if faces_color != None:
        resetFaceColor()

def subdivide():
    global faces,current_corner
    n = len(faces) * 3
    new_index = [-1] * n
    for c in range(n):
        if new_index[c] < 0:
            p1 = cornerVertex(nextCorner(c))
            p2 = cornerVertex(prevCorner(c))
            p = (p1 + p2) * 0.5
            i = len(vertices)
            new_index[c] = i
            new_index[opposite_corner[c]] = i
            vertices.append(p)
        
    new_faces = []
    c = 0
    for f in faces:
        index1 = f[0]
        index2 = f[1]
        index3 = f[2]
        new_index1 = new_index[c]
        new_index2 = new_index[c+1]
        new_index3 = new_index[c+2]
        new_faces.append([index1,new_index3,new_index2])
        new_faces.append([index2,new_index1,new_index3])
        new_faces.append([index3,new_index2,new_index1])
        new_faces.append([new_index1,new_index2,new_index3])
        c += 3

    face = cornerFace(current_corner)
    index = current_corner - face * 3
    current_corner = face * 4 * 3 + index * 3

    faces = new_faces
    onMeshChanged()



# initalize things
def setup():
    size (800, 800, OPENGL)
    frameRate(30)
    noStroke()

# draw the current mesh (you will modify parts of this routine)
def draw():
    
    background (100, 100, 180)    # clear the screen to black

    perspective (PI*0.2, 1.0, 0.01, 1000.0)
    camera (0, 0, 6, 0, 0, 0, 0, 1, 0)    # place the camera in the scene
    
    # create an ambient light source
    ambientLight (102, 102, 102)

    # create two directional light sources
    lightSpecular (202, 202, 202)
    directionalLight (100, 100, 100, -0.7, -0.7, -1)
    directionalLight (152, 152, 152, 0, 0, -1)
    
    pushMatrix();

    stroke (0)                    # draw polygons with black edges
    fill (200, 200, 200)          # set the polygon color to white
    ambient (200, 200, 200)
    specular (0, 0, 0)            # turn off specular highlights
    shininess (1.0)
    applyMatrix (rot_mat)   # rotate the object using the global rotation matrix

    # THIS IS WHERE YOU SHOULD DRAW YOUR MESH
    
    beginShape(TRIANGLES)
    
    i = 0;
    for f in faces:
        if faces_color != None:
            fill(faces_color[i])
        v1 = vertices[f[0]];
        v2 = vertices[f[1]];
        v3 = vertices[f[2]];
        vertex (v1.x,v1.y,v1.z)
        vertex (v2.x,v2.y,v2.z)
        vertex (v3.x,v3.y,v3.z)
        i+=1
    endShape(CLOSE)
    
    if show_corner == True and corner_mat:
        applyMatrix(corner_mat)
        noStroke()
        fill(255,0,0)
        sphere(1)
    
    popMatrix()

    
# read in a mesh file (this needs to be modified)
def read_mesh(filename):
    fname = "data/" + filename
    # read in the lines of a file
    with open(fname) as f:
        lines = f.readlines()

    # determine number of vertices (on first line)
    words = lines[0].split()
    num_vertices = int(words[1])
    #print "number of vertices =", num_vertices

    # determine number of faces (on first second)
    words = lines[1].split()
    num_faces = int(words[1])
    #print "number of faces =", num_faces

    # read in the vertices
    global vertices
    vertices = [];
    for i in range(num_vertices):
        words = lines[i+2].split()
        x = float(words[0])
        y = float(words[1])
        z = float(words[2])
        v = PVector(x, y, z)
        vertices.append(v) 

    # read in the faces
    global faces
    faces = []
    for i in range(num_faces):
        j = i + num_vertices + 2
        words = lines[j].split()
        nverts = int(words[0])
        if (nverts != 3):
            print "error: this face is not a triangle"
            exit()

        index1 = int(words[1])
        index2 = int(words[2])
        index3 = int(words[3])
        faces.append([index1,index2,index3])
        
    global current_corner
    current_corner = 0
    onMeshChanged()

# make sure proper error messages get reported when handling key presses
def keyPressed():
    try:
        handleKeyPressed()
    except Exception:
        traceback.print_exc()

# process key presses (call your own routines!)
def handleKeyPressed():
    if key == '1':
        read_mesh ('tetra.ply')
    elif key == '2':
        read_mesh ('octa.ply')
    elif key == '3':
        read_mesh ('icos.ply')
    elif key == '4':
        read_mesh ('star.ply')
    elif key == 'q': # quit the program
        exit()
    elif len(faces) > 0:
        if key == 'n': # next
            global current_corner
            current_corner = nextCorner(current_corner)
            resetCornerMatrix()
        elif key == 'p': # previous
            global current_corner
            current_corner = prevCorner(current_corner)
            resetCornerMatrix()
        elif key == 'o': # opposite
            global current_corner
            current_corner = opposite_corner[current_corner]
            resetCornerMatrix()
        elif key == 's': # swing
            global current_corner
            c = nextCorner(current_corner)
            c = opposite_corner[c]
            current_corner = nextCorner(c)
            resetCornerMatrix()
        elif key == 'd': # subdivide mesh
            subdivide()
        elif key == 'i': # inflate mesh
            inflate()
        elif key == 'r': # toggle random colors
            global faces_color
            if faces_color == None:
                resetFaceColor()
            else:
                faces_color = None
        elif key == 'c': # toggle showing current corner
            global show_corner
            show_corner = not show_corner
    
# remember where the user first clicked
def mousePressed():
    global mouseX_old, mouseY_old
    mouseX_old = mouseX
    mouseY_old = mouseY

# change the object rotation matrix while the mouse is being dragged
def mouseDragged():
    global rot_mat
    global mouseX_old, mouseY_old
    
    if (not mousePressed):
        return
    
    dx = mouseX - mouseX_old
    dy = mouseY - mouseY_old
    dy *= -1

    len = sqrt (dx*dx + dy*dy)
    if (len == 0):
        len = 1
    
    dx /= len
    dy /= len
    rmat = PMatrix3D()
    rmat.rotate (len * 0.005, dy, dx, 0)
    rot_mat.preApply (rmat)

    mouseX_old = mouseX
    mouseY_old = mouseY


    
