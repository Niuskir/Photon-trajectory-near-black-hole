import time
import datetime
import bpy
import math
import numpy as np
from random import random
import colorsys

# start time recording
start = time.time()
    
"""Initialization of variables & constants"""
#----------------------------
#add input equation of u2 in symbolic ?
c=1                             # speed of light in a vacuum
G=1                             # Newton constant
M=1                             # Black hole mass
distance_max=1                  # Multiple of D allowing to stop the simulation before the divergence
dphi = 10**(-3)                 # Phi interval << 1 (10 ^ -4) to avoid discrepancies
ITERATION=int(3*math.pi/dphi)   # Number of points to calculate (greater than 2pi because some orbits can go beyond a full revolution)
Rs = 2*G*M/c**2                 # Schwarzschild radius
stroke_thickness=20             # Thickness of Grease pencil stroke (photon trajectory)
trajectory_spread=0.1           # Distance between strokes (photon trajectories)
trajectories=40                 # Number of photon trajectories
trajectory_angle=26.5           # Angle 

phi_initial=0

"""Euler integration"""
#----------------------------
def euler(dist,angle):
    angle=angle*math.pi/180     #change to radian for the tan function
    if angle==0:                #avoids the division by zero error
        angle=0.01
    """
    u=variable associated with the initial position (u is multiply by iteration to 
    fill all the boxes in the list and allow faster calculation thereafter)
    """
    u=[1/dist]*ITERATION
    u1=1/(dist*math.tan(angle)) #u1=Variable associated with the initial direction
    
    ITERATION_REEL=0
    for i in range(ITERATION-1):#we perform one iteration less because the calculation gives 
                                #us the value i + 1
        ITERATION_REEL+=1
        u2=3/2*Rs*u[i]**2-u[i]  #calculation of d²u / dɸ² approximate from geodesic equations 
                                #and initial conditions (u = 1 / r)
        u1=u1+u2*dphi           #approximate du / dɸ calculation
        u[i+1]=u[i]+u1*dphi     #calculating approximate u(ɸ) (approxim)
        
        #condition which stops the calculation if the particle enters the
        #Schwarzschild Radius or if the distance to the black hole is too 
        #great (divergence)
        if 1/u[i+1]<=Rs or 1/u[i+1]>distance_max*dist:
            break  

    """
    Creation of phi and r from the values ​​of u entered (it is necessary to reduce 
    the size of the lists because the list u is never filled because of the stop conditions)
    """
    phi=[phi_initial]*ITERATION_REEL       
    r=[dist]*ITERATION_REEL
    x=[0]*ITERATION_REEL
    y=[0]*ITERATION_REEL
    for i in range(ITERATION_REEL-1):
        phi[i+1]=phi[i]+dphi
        r[i+1]=1/u[i]       
        # Converting Polar Coordinate to Cartesian Coordinates
        x[i] = r[i] * math.cos(phi[i])
        y[i] = r[i] * math.sin(phi[i])

    return x,y,ITERATION_REEL #allows you to retrieve the x and y lists of coordinates for analysis while forgetting the other variables used in the e function

def get_grease_pencil(gpencil_obj_name='GPencil') -> bpy.types.GreasePencil:
    """
    Return the grease-pencil object with the given name. Initialize one if not already present.
    :param gpencil_obj_name: name/key of the grease pencil object in the scene
    """

    # If present already, delete grease pencil object 
    if gpencil_obj_name in bpy.context.scene.objects:
        bpy.data.objects[gpencil_obj_name].select_set(True) 
        bpy.ops.object.delete()
        
    # Create brand new grease pencil object
    bpy.ops.object.gpencil_add(location=(0, 0, 0), type='EMPTY')
    # Rename grease pencil object
    bpy.context.scene.objects[-1].name = gpencil_obj_name
        
    
    # Get grease pencil object
    gpencil = bpy.context.scene.objects[gpencil_obj_name]

    return gpencil


def get_grease_pencil_layer(gpencil: bpy.types.GreasePencil, gpencil_layer_name='GP_Layer',
                            clear_layer=False) -> bpy.types.GPencilLayer:
    """
    Return the grease-pencil layer with the given name. Create one if not already present.
    :param gpencil: grease-pencil object for the layer data
    :param gpencil_layer_name: name/key of the grease pencil layer
    :param clear_layer: whether to clear all previous layer data
    """

    # Get grease pencil layer or create one if none exists
    if gpencil.data.layers and gpencil_layer_name in gpencil.data.layers:
        gpencil_layer = gpencil.data.layers[gpencil_layer_name]
    else:
        gpencil_layer = gpencil.data.layers.new(gpencil_layer_name, set_active=True)

    if clear_layer:
        gpencil_layer.clear()  # clear all previous layer data

    return gpencil_layer

# Util for default behavior merging previous two methods
def init_grease_pencil(gpencil_obj_name, gpencil_layer_name='GP_Layer',
                       clear_layer=True) -> bpy.types.GPencilLayer:
    gpencil = get_grease_pencil(gpencil_obj_name)
    gpencil_layer = get_grease_pencil_layer(gpencil, gpencil_layer_name, clear_layer=clear_layer)
    return gpencil_layer

def draw_line(gp_frame, x: tuple, y: tuple, sizexy, mat_slot: int):
    # Init new stroke
    gp_stroke = gp_frame.strokes.new()
    gp_stroke.display_mode = '3DSPACE'     # allows for editing
    gp_stroke.material_index = mat_slot  # assign material slot to stroke 
    
    # Add new stroke geometry (photon trajectory)
    gp_stroke.points.add(count=sizexy-1)    
    for i in range(0,sizexy-1):
        gp_stroke.points[i].co = (x[i],y[i],0)
    return gp_stroke

def draw_circle(gp_frame, center: tuple, radius: float, segments: int):
    # Init new stroke
    gp_stroke = gp_frame.strokes.new()
    gp_stroke.display_mode = '3DSPACE'  # allows for editing
    gp_stroke.draw_cyclic = True        # closes the stroke
    
    # Define stroke geometry
    angle = 2*math.pi/segments  # angle in radians
    gp_stroke.points.add(count=segments)
    for i in range(segments):
        x = center[0] + radius*math.cos(angle*i)
        y = center[1] + radius*math.sin(angle*i)
        z = center[2]
        gp_stroke.points[i].co = (x, y, z)

    return gp_stroke

def assign_material(material_name, color: tuple):
    # Create material for grease pencil
    ob = bpy.context.active_object
    # Get material
    mat = bpy.data.materials.get(material_name)
    # if material does not exist, create it
    if mat is None:
        mat = bpy.data.materials.new(name=material_name)
        bpy.data.materials.create_gpencil_data(mat)
        mat.grease_pencil.color = color
    # if not grease pencil material, add gp data
    if not mat.is_grease_pencil:
        bpy.data.materials.create_gpencil_data(mat)
    # fill gp with black
    mat.grease_pencil.show_fill = True
    mat.grease_pencil.fill_color = (0.107, 0.107, 0.107, 1)
    # Assign material to object
    ob.data.materials.append(mat)

"""
The method below creates or updates a number (qty_trajectories) of materials and appends them to 
the active gp object material slot list. The diffuse color steps trough HSV Hue value from 
0 to 1 in equal steps depending on the qty of materials created (equals the number of photon 
trajectories). 
"""
def stroke_materials(qty_trajectories: int):
    ob = bpy.context.active_object
    
    for i in range(qty_trajectories):
        # Create material for grease pencil
        material_name = "color_%i" % i
        if "color_%i" % i in bpy.data.materials.keys():       # if material already exists 
            gp_mat = bpy.data.materials["color_%i" % i]       # get it
        else:
            gp_mat = bpy.data.materials.new("color_%i" % i)   # create a new material

        if not gp_mat.is_grease_pencil:
            bpy.data.materials.create_gpencil_data(gp_mat)
        
        color_step=1/qty_trajectories                         # determine hue color step size
        rgb=colorsys.hsv_to_rgb(color_step*i,1,1)             # convert HSV to RGB
        gp_mat.grease_pencil.color = (rgb[0],rgb[1],rgb[2],1) # set color 

        ob.data.materials.append(gp_mat)                      # add material to a new material slot    
        
"""********Draw Schwarzschild Radius******"""
gp_layer = init_grease_pencil('schwarzschild_radius')
frame=0
gp_frame = gp_layer.frames.new(frame)
draw_circle(gp_frame, (0,0,0), Rs, 32)

# Assign Material to Grease pencil object "schwarzschild_radius"
assign_material("Red",(1, 0.147417, 0.0325291, 1))

# Set stroke thickness
bpy.context.object.data.layers["GP_Layer"].line_change = stroke_thickness

# Deselect Greasepencil object
bpy.ops.object.select_all(action='DESELECT')

"""*********Draw photon trajectories***********"""
gp_layer = init_grease_pencil('photon_trajectories')
frame=0
gp_frame = gp_layer.frames.new(frame)
stroke_materials(trajectories)
for D in range(0,trajectories,1):
    x,y,sizexy=euler(10+D*trajectory_spread,trajectory_angle)
    draw_line(gp_frame, x, y, sizexy, D)

# Set stroke thickness
bpy.context.object.data.layers["GP_Layer"].line_change = stroke_thickness

# Add Build modifier for redering purposes
bpy.ops.object.gpencil_modifier_add(type='GP_BUILD')
bpy.context.object.grease_pencil_modifiers["Build"].start_delay = 1
bpy.context.object.grease_pencil_modifiers["Build"].mode = 'CONCURRENT'
bpy.context.object.grease_pencil_modifiers["Build"].length = 150
bpy.context.object.grease_pencil_modifiers["Build"].show_viewport = False
bpy.context.object.grease_pencil_modifiers["Build"].show_render = False


# Deselect Greasepencil object
bpy.ops.object.select_all(action='DESELECT')
#*********************************************
# determine elapsed time 
elapsed = time.time()-start
elapsed =round(elapsed)
conversion = datetime.timedelta(seconds=elapsed)
converted_time = str(conversion)
print("Elapsed Time %r"%converted_time)