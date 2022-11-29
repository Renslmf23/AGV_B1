from scipy import signal
import matplotlib.pyplot as plt

num = [1]
den = [1, 1, 0]  # s^2 + s
A, B, C, D = signal.tf2ss(num, den)

print(A, B, C, D)

t, y = signal.step((A, B, C, D))
plt.plot(t, y, label="Step")
t, y = signal.impulse((A, B, C, D))
plt.plot(t, y, label="Impulse")
plt.xlabel('Time [s]')

plt.ylabel('Amplitude')

plt.title('Step and impulse response')
plt.legend()

plt.grid()
plt.show()


