import math
import numpy as np
from numpy import sin,cos,pi
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import os

# Constantes

M1 = 2          # Masse du pendule 1 (kg)
M2 = 2          # Masse du pendule 2 (kg)
L1 = 1          # Longueur du pendule 1 (m)
L2 = 1          # Longueur du pendule 2 (m)
b = 0.5          # Coefficient d'amortissement
G = 9.81        # Accélération gravitationnelle en m/s^2

# Calcul de la force
def derivs(t,state):
    theta1 = state[0]
    dtheta1 = state[1]
    theta2 = state[2]
    dtheta2 = state[3]

    delta = theta1-theta2

    NUM_T1 = -(b/M1)*dtheta1 + (-M2*cos(delta)*L1*(dtheta1**2)*sin(delta) + M2*cos(delta)*G*sin(theta2) - M2*L2*(dtheta2**2)*sin(delta) - (M1+M2)*G*sin(theta1)) 
    DEN_T1 = L1*(M1+M2-(M2*(cos(delta))**2))
    d2theta1 = NUM_T1/DEN_T1

    NUM_T2 = -(b/M2)*dtheta2 +(M1+M2)*((L1*(dtheta1**2)*sin(delta))+(((dtheta2**2)*sin(delta)*cos(delta)*M2*L2)/(M1+M2))+(cos(delta)*G*sin(theta1))-(G*sin(theta2)))
    DEN_T2 = L2*(M1+(M2*(sin(delta))**2))
    d2theta2 = NUM_T2/DEN_T2

    return [dtheta1, d2theta1, dtheta2, d2theta2]
# Conditions initiales

step = 0.05        # Échelons de temps
starttime = 0          # Temps de départ (s)
endTime = 120         # Temps de fin (s)

def initvalues(theta1,dtheta1,theta2,dtheta2):
    initvalues = [theta1,dtheta1,theta2,dtheta2]
    return initvalues

tspan = [0, endTime+step]
t = np.arange(starttime,endTime+step,step)
nb_points = len(t)
l = np.arange(0,nb_points,1)

initvalues1 = initvalues(pi,0,0,0)
initvalues2 = initvalues(pi+0.000000000000001,0,0,0)

# Résolution pour chaque point de temps

out_values1 = solve_ivp(derivs,tspan,initvalues1,t_eval=t)
out_values2 = solve_ivp(derivs,tspan,initvalues2,t_eval=t)


theta1_out1 = out_values1.y[0,:]
dtheta1_out1 = out_values1.y[1,:]
theta2_out1 = out_values1.y[2,:]
dtheta2_out1 = out_values1.y[3,:]

theta1_out2 = out_values2.y[0,:]
dtheta1_out2 = out_values2.y[1,:]
theta2_out2 = out_values2.y[2,:]
dtheta2_out2 = out_values2.y[3,:]

x11 = L1*np.sin(theta1_out1)
y11 = -L1*np.cos(theta1_out1)
x21 = L2*np.sin(theta2_out1) + x11
y21 = -L2*np.cos(theta2_out1) + y11

x12 = L1*np.sin(theta1_out2)
y12 = -L1*np.cos(theta1_out2)
x22 = L2*np.sin(theta2_out2) + x12
y22 = -L2*np.cos(theta2_out2) + y12

# Représentation visuelle

# plt.figure(1)
# plt.plot(t,theta1_out1,label='angular displacement pendulum #1 (rad)')
# plt.xlabel('Time (s)')
# plt.legend()
# plt.figure(2)
# plt.plot(t,theta2_out1,label='angular displacement pendulum #2 (rad)')
# plt.xlabel('Time (s)')
# plt.legend()
# plt.show()


fig = plt.figure()
ax = fig.add_subplot(111, autoscale_on=False, xlim=(-2, 2), ylim=(-2, 2))
ax.grid()

line1, = ax.plot([], [], 'o-', lw=2,c='b')
line2, = ax.plot([], [], 'o-', lw=2,c='r')
foo, = plt.plot([],[],'-',color='g')
time_template = 'time = %.1fs'
time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)
foox = []
fooy = []



def init():
    line1.set_data([], [])
    line2.set_data([], [])
    foo.set_data([], [])
    time_text.set_text('')
    return line1, line2, time_text


def animate(i):
    thisx1 = [0, x11[i], x21[i]]
    thisx2 = [0, x12[i], x22[i]]
    thisy1 = [0, y11[i], y21[i]]
    thisy2 = [0, y12[i], y22[i]]

    #foox.append(x2[i])
    #fooy.append(y2[i])     

    line1.set_data(thisx1, thisy1)
    line2.set_data(thisx2, thisy2)
    #foo.set_data(foox, fooy)
    time_text.set_text(time_template % (i*step))
    return line1, line2, time_text#, foo

ani = animation.FuncAnimation(fig, animate, np.arange(1, len(theta1_out1)),interval=25, blit=True, init_func=init)

# ani.save('double_pendulum.mp4', fps=15)
plt.show()