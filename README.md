# Photon-trajectory-near-black-hole
Photon trajectory calculation and visualization in 2D and 3D using Python scripting in Blender 3D software

A python script in Blender version 2.82a(2D) and version 2.83(3D) is used to calculate the x and y coordinates of the trajectories of photons traveling towards a black hole and create Blender Grease Pencil objects to visualize the Schwartzschiel Radius and the photon trajectories. 

Blender is the free and open source 3D creation suite. It supports the entirety of the 3D pipeline—modeling, rigging, animation, simulation, rendering, compositing and motion tracking, video editing and 2D animation pipeline.

How to use:
1) Download and install the latest Blender software here: www.blender.org. 
2) For 2D simulation download the blend file "deviation_of_light_near_a_black_hole.blend" and open it with Blender. For 3D simulation download the blend file "deviation_of_light_near_a_black_hole_3D for git.blend" and open it with Blender version 2.83 or above. 

The python script (is part of the blend file) contains parameters near the top you can play around with to get different trajectories. Each time you run the script, the existing Grease Pencil objects are deleted and new ones are created based on the parameters in the script. 

Blender is a very powerful 3D creation suite so if you know Blender you can go all out with this.

I am not a professional programmer so many things in the python script could have been done more efficient i am sure.

Use this anyway you want. Hopefully it is worthwile for someone. 

The Python method used calculate the trajectories (Euler) was found in the file "only_trajectories_with_euler.py" which you can find in this Github repository:
https://github.com/Python-simulation/Black-hole-simulation-using-python

These Youtube videos were made completely in Blender: 
2D trajectories: https://youtu.be/rbo4uJvEOj0
3D trajectories: https://youtu.be/PIQx-puuWCg
