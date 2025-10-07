import sys
import math
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from collections import deque
import numpy as np

# ----- CONFIG -----
PORT = '/dev/cu.usbmodem1101'  # <- change if needed
BAUD = 115200
WINDOW = 200                   # number of samples shown

ser = serial.Serial(PORT, BAUD, timeout=1)

pitch_buf = deque(maxlen=WINDOW)
roll_buf  = deque(maxlen=WINDOW)
x_idx     = deque(maxlen=WINDOW)

# ----- FIGURE -----
fig = plt.figure(figsize=(10,6))

# Top: Time-series plot
ax1 = fig.add_subplot(2,1,1)
(line_pitch,) = ax1.plot([], [], label="Pitch (°)")
(line_roll,)  = ax1.plot([], [], label="Roll (°)")
ax1.set_xlim(0, WINDOW)
ax1.set_ylim(-90, 90)
ax1.set_xlabel("Samples")
ax1.set_ylabel("Angle (°)")
ax1.set_title("MPU6050 Pitch & Roll (Time-series)")
ax1.legend(loc="upper right")

# Bottom: 3D tilt visualization
ax2 = fig.add_subplot(2,1,2, projection='3d')
ax2.set_xlim([-1,1])
ax2.set_ylim([-1,1])
ax2.set_zlim([-0.5,0.5])
ax2.set_xlabel("X")
ax2.set_ylabel("Y")
ax2.set_zlabel("Z")
ax2.set_title("MPU6050 Tilt (Pitch & Roll)")

# Create a rectangular “device” centered at origin
def create_box():
    # 8 corners of a box
    l, w, h = 1.0, 0.2, 0.1
    corners = np.array([
        [ l/2,  w/2,  h/2],
        [ l/2, -w/2,  h/2],
        [-l/2, -w/2,  h/2],
        [-l/2,  w/2,  h/2],
        [ l/2,  w/2, -h/2],
        [ l/2, -w/2, -h/2],
        [-l/2, -w/2, -h/2],
        [-l/2,  w/2, -h/2],
    ])
    return corners

box_corners = create_box()

# Plot edges
edges = [
    [0,1],[1,2],[2,3],[3,0],  # top
    [4,5],[5,6],[6,7],[7,4],  # bottom
    [0,4],[1,5],[2,6],[3,7]   # verticals
]
lines = [ax2.plot([], [], [], 'b')[0] for _ in edges]

# ----- FUNCTIONS -----
def rotation_matrix(pitch_deg, roll_deg):
    pitch = math.radians(pitch_deg)
    roll  = math.radians(roll_deg)
    # Rotation around X (roll) then Y (pitch)
    Rx = np.array([[1,0,0],
                   [0,math.cos(roll), -math.sin(roll)],
                   [0, math.sin(roll), math.cos(roll)]])
    Ry = np.array([[math.cos(pitch),0, math.sin(pitch)],
                   [0,1,0],
                   [-math.sin(pitch),0, math.cos(pitch)]])
    return Ry @ Rx

def parse_line(line):
    try:
        parts = line.strip().split(',')
        if len(parts) != 2:
            return None, None
        pitch = float(parts[0])
        roll  = float(parts[1])
        return pitch, roll
    except:
        return None, None

def init():
    line_pitch.set_data([], [])
    line_roll.set_data([], [])
    for line in lines:
        line.set_data([], [])
        line.set_3d_properties([])
    return [line_pitch, line_roll]+lines

def update(frame):
    # Read a few lines from serial
    for _ in range(5):
        raw = ser.readline().decode(errors='ignore')
        if not raw:
            break
        pitch, roll = parse_line(raw)
        if pitch is None:
            continue
        pitch_buf.append(pitch)
        roll_buf.append(roll)
        x_idx.append(len(x_idx) + 1 if x_idx else 1)

    # Update time-series
    xs = list(range(len(x_idx)))
    line_pitch.set_data(xs, list(pitch_buf))
    line_roll.set_data(xs, list(roll_buf))
    ax1.set_xlim(max(0, len(xs)-WINDOW), max(WINDOW, len(xs)))

    # Update 3D tilt
    if pitch_buf:
        R = rotation_matrix(pitch_buf[-1], roll_buf[-1])
        rotated = (R @ box_corners.T).T
        for i, edge in enumerate(edges):
            start, end = edge
            x = [rotated[start,0], rotated[end,0]]
            y = [rotated[start,1], rotated[end,1]]
            z = [rotated[start,2], rotated[end,2]]
            lines[i].set_data(x, y)
            lines[i].set_3d_properties(z)

    return [line_pitch, line_roll]+lines

# ----- ANIMATION -----
ani = animation.FuncAnimation(fig, update, init_func=init, interval=30, blit=True)
plt.tight_layout()
plt.show()
