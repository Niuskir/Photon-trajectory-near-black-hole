import time
import datetime
import bpy
import math
from math import sin, cos
import numpy as np
from random import random
import colorsys



# start time recording
start = time.time()

#=================================================================================================    
"""Initialization of variables & constants"""
c=1                             # speed of light in a vacuum
G=1                             # Newton constant
M=1                             # Black hole mass
distance_max=1                  # Multiple of D allowing to stop the simulation before the divergence
dphi = 10**(-6)                 # Phi interval << 1 (10 ^ -4) to avoid discrepancies (error margin)
points=int(3*math.pi/dphi)      # Number of points to calculate (greater than 2pi because some orbits can go beyond a full revolution)
skip=1000                       # Number of calculation interations to skip to reduce script running time
iteration=int(points/skip)           
Rs = 2*G*M/c**2                 # Schwarzschild radius
stroke_thickness=30             # Thickness of Grease pencil stroke (photon trajectory)
trajectories=20                 # Number of photon trajectories to generate 

'''start location and direction of photon trajecttory'''
D=40                            # Distance between Swartzschild radius midpoint and startpoint photon trajectory 
trajectory_angle=7.7            # Initial direction of photon in degrees (= angle along line to sphere midpoint) 
phi_initial=20                  # Angle in degrees between line D and x-axis  
'''=================================================='''

activate_build_modifier=True   # Activate the Build Modifier attached to trajectories (True/False)


#================================================================================================
"""Euler integration, represents the differential equation : d²u(ɸ)/dɸ²=3/2*Rs*u²(ɸ)-u(ɸ)"""
def euler(dist,phi_initial,angle):
    angle=angle*math.pi/180                 #change to radian for the tan function
    phi_initial=phi_initial*math.pi/180     #change to radian for the tan function
    if angle==0:                            #avoids the division by zero error
        angle=0.01
    """
    u=variable associated with the initial position (u is multiply by iteration to 
    fill all the boxes in the list and allow faster calculation thereafter)
    """
    u=[1/dist]*iteration        #define array u with initial condition 1/r filled
    u1=1/(dist*math.tan(angle)) #u1=Variable associated with the initial direction
    
    iteration_reel=0
    for i in range(iteration-1):#we perform one iteration less because the calculation gives 
                                #us the value i + 1
        iteration_reel+=1
        u2=3/2*Rs*u[i]**2-u[i]  #calculation of d²u / dɸ² approximate from geodesic equations 
                                #and initial conditions (u = 1 / r)
        u1=u1+u2*dphi*skip           #approximate du / dɸ calculation
        u[i+1]=u[i]+u1*dphi*skip     #calculating approximate u(ɸ) (approxim)
        
        #condition which stops the calculation if the particle enters the
        #Schwarzschild Radius or if the distance to the black hole is too 
        #great (divergence)
        if 1/u[i+1]<=Rs or 1/u[i+1]>distance_max*dist:
            break  

    """
    Creation of phi and r from the values ​​of u entered (it is necessary to reduce 
    the size of the lists because the list u is never filled because of the stop conditions)
    """
    phi=[phi_initial]*iteration_reel       
    r=[dist]*iteration_reel
    xyz=[[0 for i in range(3)] for j in range(iteration_reel)]
    for i in range(iteration_reel-1):
        phi[i+1]=phi[i]+dphi*skip
        r[i+1]=1/u[i]       
        # Converting Polar Coordinate to Cartesian Coordinates
        xyz[i]=(r[i] * math.cos(phi[i]), r[i] * math.sin(phi[i]), 0)
        if trajectories != 1:
            xyz[i]=rotate(xyz[i],rotation_angle_x,"x")
            xyz[i]=rotate(xyz[i],rotation_angle_y,"y")
            xyz[i]=rotate(xyz[i],rotation_angle_z,"z")

    return iteration_reel,xyz #allows you to retrieve the x and y lists of coordinates for analysis while forgetting the other variables used in the e function

#====================================================================================================
def rotate(X, theta, axis):
  '''Rotate multidimensional array `X` `theta` degrees around axis `axis`'''
  theta=theta*math.pi/180
  c, s = np.cos(theta), np.sin(theta)
  if axis == 'x': return np.dot(X, np.array([
    [1.,  0,  0],
    [0 ,  c, -s],
    [0 ,  s,  c]
  ]))
  elif axis == 'y': return np.dot(X, np.array([
    [c,  0,  -s],
    [0,  1,   0],
    [s,  0,   c]
  ]))
  elif axis == 'z': return np.dot(X, np.array([
    [c, -s,  0 ],
    [s,  c,  0 ],
    [0,  0,  1.],
  ]))
                     
#===================================================================================================
def get_grease_pencil(gpencil_obj_name='GPencil') -> bpy.types.GreasePencil:
    """
    Initialize grease pencil and return the object with the given name. 
    :param gpencil_obj_name: name/key of the grease pencil object in the scene
    """
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    
    # Create brand new grease pencil object
    bpy.ops.object.gpencil_add(location=(0, 0, 0), type='EMPTY')
    # Rename grease pencil object
    bpy.context.scene.objects[-1].name = gpencil_obj_name
        
    
    # Get grease pencil object
    gpencil = bpy.context.scene.objects[gpencil_obj_name]

    return gpencil

#=====================================================================================================
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

#======================================================================================================
# Util for default behavior merging previous two methods
def init_grease_pencil(gpencil_obj_name, gpencil_layer_name='GP_Layer',
                       clear_layer=True) -> bpy.types.GPencilLayer:
    gpencil = get_grease_pencil(gpencil_obj_name)
    gpencil_layer = get_grease_pencil_layer(gpencil, gpencil_layer_name, clear_layer=clear_layer)
    return gpencil_layer

#=======================================================================================================
# Generate Grease Pencil object strokes
def draw_line(gp_frame, sizexyz, mat_slot: int, xyz):
    # Init new stroke
    gp_stroke = gp_frame.strokes.new()
    gp_stroke.display_mode = '3DSPACE'     # allows for editing
#    gp_stroke.material_index = mat_slot  # assign material slot to stroke 

    # Add new stroke geometry (photon trajectory)
    gp_stroke.points.add(count=sizexyz-1)    
    for i in range(0,sizexyz-1):
        gp_stroke.points[i].co = (xyz[i])
    return gp_stroke

#=======================================================================================================
# Rotate the generated GP strokes (photon trajectories)
def rotate_stroke(stroke, angle, axis):
    # Define rotation matrix based on axis
    if axis.lower() == 'x':
        transform_matrix = np.array([[1, 0, 0],
                                     [0, cos(angle), -sin(angle)],
                                     [0, sin(angle), cos(angle)]])
    elif axis.lower() == 'y':
        transform_matrix = np.array([[cos(angle), 0, -sin(angle)],
                                     [0, 1, 0],
                                     [sin(angle), 0, cos(angle)]])
    # default on z
    else:
        transform_matrix = np.array([[cos(angle), -sin(angle), 0],
                                     [sin(angle), cos(angle), 0],
                                     [0, 0, 1]])

    # Apply rotation matrix to each point
    for i, p in enumerate(stroke.points):
        p.co = transform_matrix @ np.array(p.co).reshape(3, 1)

#========================================================================================================
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

#=========================================================================================================
# Assign material to sphere (Schwartzschild Radius)
def assign_material_mesh(material_name, color: tuple):
    ob = bpy.context.active_object
    # Get material
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name=material_name).diffuse_color=color
        bpy.data.materials.use_nodes = True
        bpy.ops.node.add_node(type="ShaderNodeMixShader", use_transform=True)
        bpy.ops.node.select(wait_to_deselect_others=True, mouse_x=727, mouse_y=294, extend=False,deselect_all=True)
        bpy.ops.node.link(detach=False)
        bpy.ops.node.add_node(type="ShaderNodeBsdfTransparent", use_transform=True)
        bpy.ops.node.select(wait_to_deselect_others=True, mouse_x=480, mouse_y=230, extend=False, deselect_all=True)
        bpy.ops.node.link(detach=False)
        bpy.data.materials["photon_sphere_mat"].node_tree.nodes["Mix Shader"].inputs[0].default_value = 0.8
    mat.diffuse_color=color
    # Assign it to object
    if ob.data.materials:
        # assign to 1st material slot
        ob.data.materials[0] = mat
    else:
        # no slots
        ob.data.materials.append(mat)

#==========================================================================================================
    """ Create material for grease pencil """
def assign_material_gp(material_name,gp_name):
    if material_name in bpy.data.materials.keys():
        gp_mat = bpy.data.materials[material_name]
    else:
        gp_mat = bpy.data.materials.new(material_name)
        
    if not gp_mat.is_grease_pencil:
        bpy.data.materials.create_gpencil_data(gp_mat)
        gp_mat.grease_pencil.color = (1, 0, 0.818649, 1)
    #get grease pencil
    ob = bpy.context.active_object
    # Assign the material to the grease pencil 
    ob.data.materials.append(gp_mat)

#==========================================================================================================
"""
The method below creates or updates a number (qty_trajectories) of materials and appends them to 
the active gp object material slot list. The diffuse color is the HSV Hue value from 
0 to 1 chosen randomly. 
"""
def stroke_materials(qty_trajectories: int):
    ob = bpy.context.active_object
    
    for i in range(1,qty_trajectories+1,1):
        # Create material for grease pencil
        material_name = "color_" + str(i)
        if "color_" + str(i) in bpy.data.materials.keys():       # if material already exists 
            gp_mat = bpy.data.materials.get("color_" + str(i))      # get it
        else:
            gp_mat = bpy.data.materials.new("color_" + str(i))   # create a new material

        if not gp_mat.is_grease_pencil:
            bpy.data.materials.create_gpencil_data(gp_mat)
        
        rgb=colorsys.hsv_to_rgb(random(),1,1)             # convert HSV to RGB
        gp_mat.grease_pencil.color = (rgb[0],rgb[1],rgb[2],1) # set color 

#        ob.data.materials.append(gp_mat)                      # add material to a new material slot    

#=========================================================================================================        
def draw_schwarzschild_radius():
    """********Draw Schwarzschild Radius******"""
    # Delete old and create new sphere (Schwarzschild Radius)
    obj_name = "schwarzschild_radius"
    if obj_name in bpy.context.scene.objects:
        objs = bpy.data.objects
        objs.remove(objs[obj_name], do_unlink=True)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=Rs, location=(0, 0, 0))
    bpy.context.object.name = obj_name
    

    # Assign Material to Grease pencil object "schwarzschild_radius"
    assign_material_mesh("black_hole_mat",(0.027, 0.027, 0.027, 1))

    bpy.ops.object.shade_smooth()
    print('schwarzschild_radius sphere created')
    # Deselect object
    bpy.ops.object.select_all(action='DESELECT')

#==========================================================================================================
def draw_photon_sphere():
    """********Delete old photon sphere and draw new one. The photon sphere is a spherical region of """
    """space where gravity is strong enough that photons (light particles) are forced to travel in orbits."""
    sphere_name='photon_sphere'
    if sphere_name in bpy.context.scene.objects:
        objs = bpy.data.objects
        objs.remove(objs[sphere_name], do_unlink=True)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=Rs*1.5, enter_editmode=False, location=(0, 0, 0))
    bpy.context.object.name = sphere_name
    
    # Assign Material to Grease pencil object "schwarzschild_radius"
    assign_material_mesh("photon_sphere_mat",(0.003, 0.8, 0.011, 1))

    bpy.ops.object.shade_smooth()
    print('photon_sphere created')
    # Deselect object
    bpy.ops.object.select_all(action='DESELECT')
    
#==========================================================================================================
    """*********Draw photon trajectories***********"""
def draw_photon_trajectories(stroke_number):
    gp_layer = init_grease_pencil('photon_trajectory_' + str(stroke_number))
    frame=0
    gp_frame = gp_layer.frames.new(frame)
    sizexyz,xyz=euler(D,phi_initial,trajectory_angle) # calculate x+y trajectory point locations
    draw_line(gp_frame, sizexyz, stroke_number, xyz)         # create trajectory (stroke) from points in xyz
    assign_material_gp("color_" + str(stroke_number),'photon_trajectory_' + str(stroke_number))
    # Set stroke thickness
    bpy.context.object.data.layers["GP_Layer"].line_change = stroke_thickness
    start_delay=13
    # Add Build modifier for redering purposes
    bpy.ops.object.gpencil_modifier_add(type='GP_BUILD')
    bpy.context.object.grease_pencil_modifiers["Build"].mode = 'CONCURRENT'
    bpy.context.object.grease_pencil_modifiers["Build"].length = 150
    bpy.context.object.grease_pencil_modifiers["Build"].start_delay =1+start_delay*(stroke_number-1)
    bpy.context.object.grease_pencil_modifiers["Build"].show_viewport = activate_build_modifier
    bpy.context.object.grease_pencil_modifiers["Build"].show_render = activate_build_modifier

    bpy.ops.object.gpencil_modifier_add(type='GP_BUILD')
    bpy.context.object.grease_pencil_modifiers["Build.001"].start_delay = 1
    bpy.context.object.grease_pencil_modifiers["Build.001"].mode = 'CONCURRENT'
    bpy.context.object.grease_pencil_modifiers["Build.001"].length = 150
    bpy.context.object.grease_pencil_modifiers["Build.001"].start_delay = 1+start_delay*(stroke_number-1)
    bpy.context.object.grease_pencil_modifiers["Build.001"].transition = 'FADE'
    bpy.context.object.grease_pencil_modifiers["Build.001"].show_viewport = activate_build_modifier
    bpy.context.object.grease_pencil_modifiers["Build.001"].show_render = activate_build_modifier    
      
    print('photon_trajectory_' + str(stroke_number) +' created')
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

#==========================================================================================================
    """Delete old photon trajectories"""
def delete_trajectories():    
    bpy.ops.object.select_all(action='DESELECT')
    # select all grease pencil objects 
    for ob in bpy.context.scene.objects:              
        if ob.type == 'GPENCIL' and ob.name.startswith("photon_trajectory_"):
            #Select the object
            ob.select_set(state=True)     
    #Delete all objects selected above 
    bpy.ops.object.delete()
    
#==========================================================================================================
    """Assign target to text shrinkwrap modifier"""
def assign_target(text_name,target):    
    ob = bpy.context.scene.objects[text_name]    # Get the object
    bpy.ops.object.select_all(action='DESELECT') # Deselect all objects
    bpy.context.view_layer.objects.active = ob   # Make the cube the active object 
    ob.select_set(True)                          # Select the cube
    bpy.context.object.modifiers["Shrinkwrap"].target = bpy.data.objects[target] # Assign taget

#===========================================================================================================
draw_schwarzschild_radius()                # create new schwarzschild_radius object
assign_target("text_schwarzschild_radius","schwarzschild_radius") # assign text shrinkwrap modifier target 
draw_photon_sphere()                       # create new photon_sphere object
assign_target("text_photon_sphere","photon_sphere")  # assign text shrinkwrap modifier target
delete_trajectories()                      # delete old trajectories
stroke_materials(trajectories)             # create gp materials which can be assigned to trajectories later 
stroke_number=1
for ix in range(0,trajectories,1):
    trajectory_angle=7.2+(random()*2)      # vary photon angle for each trajectory
    rotation_angle_x=random()*360          # rotate randomly
    rotation_angle_y=random()*360
    rotation_angle_z=random()*360
    draw_photon_trajectories(stroke_number)# draw trajectory (GP)
    stroke_number+=1 # keep track of trajectory number

# determine elapsed time 
elapsed = time.time()-start
elapsed =round(elapsed)
conversion = datetime.timedelta(seconds=elapsed)
converted_time = str(conversion)
print("Elapsed Time %r"%converted_time)