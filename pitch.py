import serial
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation
import time

# ----- CONFIG -----
PORT = 'COM8'  # Replace with your Arduino COM port
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

# ----- GLOBALS -----
yaw = 0.0
last_time = None

# ----- 3D ENVIRONMENT -----
fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])
ax.set_xlabel("X axis")
ax.set_ylabel("Y axis")
ax.set_zlabel("Z axis")
ax.set_title("MPU6050 Real-Time 3D Cube Visualization")
ax.set_box_aspect([1,1,1])

# Cube edges for the environment
cube_edges = [
    [(-1,-1,-1), (1,-1,-1)], [(-1,-1,-1), (-1,1,-1)], [(-1,-1,-1), (-1,-1,1)],
    [(1,1,1), (-1,1,1)], [(1,1,1), (1,-1,1)], [(1,1,1), (1,1,-1)],
    [(-1,1,-1), (-1,1,1)], [(-1,1,-1), (1,1,-1)],
    [(1,-1,-1), (1,-1,1)], [(1,-1,-1), (1,1,-1)],
    [(1,-1,1), (1,1,1)], [(-1,-1,1), (-1,1,1)]
]
for edge in cube_edges:
    xs, ys, zs = zip(*edge)
    ax.plot(xs, ys, zs, color='black')

# ----- OBJECT INSIDE THE CUBE (colored cube) -----
def create_cube(size=0.3):
    """Vertices of a cube centered at origin"""
    r = size / 2
    vertices = np.array([[-r,-r,-r],[r,-r,-r],[r,r,-r],[-r,r,-r],
                         [-r,-r,r],[r,-r,r],[r,r,r],[-r,r,r]])
    # edges as pairs of vertex indices
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    return vertices, edges

cube_vertices, cube_edges_obj = create_cube()
lines = [ax.plot([], [], [], color='cyan', linewidth=2)[0] for _ in cube_edges_obj]

# ----- FUNCTIONS -----
def read_sensor():
    """Read pitch, roll, gz (yaw rate) from Arduino and integrate yaw."""
    global yaw, last_time
    line = ser.readline().decode(errors='ignore').strip()
    try:
        pitch, roll, gz = map(float, line.split(','))
        now = time.time()
        dt = now - last_time if last_time else 0.01
        last_time = now
        yaw += gz * dt
        return pitch, roll, yaw
    except:
        return 0,0,yaw

def rotate_vertices(vertices, pitch, roll, yaw):
    """Rotate cube vertices by pitch, roll, yaw (degrees)."""
    p = np.radians(pitch)
    r = np.radians(roll)
    y = np.radians(yaw)
    
    Rx = np.array([[1,0,0],[0,np.cos(r),-np.sin(r)],[0,np.sin(r),np.cos(r)]])
    Ry = np.array([[np.cos(p),0,np.sin(p)],[0,1,0],[-np.sin(p),0,np.cos(p)]])
    Rz = np.array([[np.cos(y),-np.sin(y),0],[np.sin(y),np.cos(y),0],[0,0,1]])
    
    R = Rz @ Ry @ Rx
    rotated = (R @ vertices.T).T
    return rotated

def init():
    for line in lines:
        line.set_data([], [])
        line.set_3d_properties([])
    return lines

def update(frame):
    pitch, roll, yaw_val = read_sensor()
    rotated = rotate_vertices(cube_vertices, pitch, roll, yaw_val)
    for idx, (start, end) in enumerate(cube_edges_obj):
        xs = [rotated[start,0], rotated[end,0]]
        ys = [rotated[start,1], rotated[end,1]]
        zs = [rotated[start,2], rotated[end,2]]
        lines[idx].set_data(xs, ys)
        lines[idx].set_3d_properties(zs)
    return lines

# ----- ANIMATION -----
ani = animation.FuncAnimation(fig, update, init_func=init, interval=10, blit=False)
plt.show()
