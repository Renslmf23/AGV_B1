from scipy import signal
import control
import matplotlib.pyplot as plt

import mbrtc
from mbrtc import sim
import numpy as np


def plot_similarity(A, B, C, D):
    E = [[1, 1], [1, -1]]
    Einv = np.linalg.inv(E)
    Ae = np.matmul(np.matmul(E, A), Einv)
    Be = np.matmul(E, B)
    Ce = np.matmul(C, Einv)
    De = D
    print(A, B, C, D)
    print(Ae, Be, Ce, De)
    t, y = signal.step((Ae, Be, Ce, De))
    plt.plot(t, y, label="Step similarity")
    t, y = signal.impulse((Ae, Be, Ce, De))
    plt.plot(t, y, label="Impulse similarity")


def plot_discrete(A, B, C, D, step_label="Step", impulse_label="Impulse", X0=0):
    Ad, Bd, Cd, Dd, dtD = signal.cont2discrete((A, B, C, D), h)

    t, y = signal.dstep((Ad, Bd, Cd, Dd, dtD), x0=X0, n=round(7 / h))
    plt.plot(t, y[0], label=step_label)
    t, y = signal.dimpulse((Ad, Bd, Cd, Dd, dtD), x0=X0, n=round(7 / h))
    plt.plot(t, y[0], label=impulse_label)


def plot_continuous(A, B, C, D, step_label="Step", impulse_label="Impulse", X0=0):
    t, y = signal.step((A, B, C, D), x0=X0)
    plt.plot(t, y, label=step_label)
    t, y = signal.impulse((A, B, C, D), x0=X0)
    plt.plot(t, y, label=impulse_label)


def plot_interstate(A, B, C, D, h):
    ud = np.zeros([1, 100])
    ud[0] = 1
    td = np.linspace(0, 7, 100)
    t, y = mbrtc.sim_intersample(A, B, C, D, h, 10, ud, td)
    plt.plot(t, y, label="Impulse")


def space_state_system_generator(Ad, Bd, Cd, Dd):
    Phi = np.zeros((2, 2))
    Gamma = np.zeros((2, 1))
    C = np.zeros((1, 2))
    K = [[3]]
    Aser, Bser, Cser, Dser = mbrtc.ss_series(Ad, Bd, Cd, Dd, Phi, Gamma, C, K)
    Apar, Bpar, Cpar, Dpar = mbrtc.ss_parallel(Ad, Bd, Cd, Dd, Phi, Gamma, C, K)
    Afeed, Bfeed, Cfeed, Dfeed = mbrtc.ss_feedback(Ad, Bd, Cd, Dd, Phi, Gamma, C, K)
    plot_continuous(Aser, Bser, Cser, Dser, "Step series", "Impulse series")
    plot_continuous(Apar, Bpar, Cpar, Dpar, "Step parallel", "Impulse parallel")
    plot_continuous(Afeed, Bfeed, Cfeed, Dfeed, "Step feedback", "Impulse feedback")


def show_plot():
    plt.ylabel('Amplitude')
    plt.xlabel('Time [s]')
    plt.title('Step and impulse response')
    plt.legend()

    plt.grid()
    plt.show()


num = [1]
den = [0.12, 0.2, 0.5]  # s^2 + s
h = 0.12
A, B, C, D = signal.tf2ss(num, den)
print(A, B, C, D)
L = np.array([[1.3333, -2.16667]])
K = np.array([[1, 1]])
#K = mbrtc.place(A, B, [-7, -4])
Acl = A - B * L
Aso = A - C * K
ss_sys = control.StateSpace(Acl, B, C, D)
print(control.poles(ss_sys))

plot_discrete(A, B, C, D, "Step uncontrolled", "Impulse uncontrolled", 1)
plot_discrete(Acl, B, C, D, "Step feedback", "Impulse feedback", 1)
plot_discrete(Aso, B, C, D, "Step observer", "Impulse observer", 1)
# state_feedback_closed_loop(A, B, C, D, K)
# plot_interstate(A, B, C, D, h)
# space_state_system_generator(A, B, C, D)
show_plot()
