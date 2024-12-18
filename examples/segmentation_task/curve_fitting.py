import numpy as np
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Generate synthetic noisy 3D data
np.random.seed(42)
n_points = 100
t = np.linspace(0, 2 * np.pi, n_points)
x = np.sin(t) + np.random.normal(0, 0.1, n_points)
y = np.cos(t) + np.random.normal(0, 0.1, n_points)
z = t + np.random.normal(0, 0.1, n_points)

# Parametric spline fitting
tck, u = splprep([x, y, z], s=3)  # s is the smoothing factor
u_fine = np.linspace(0, 1, 500)
x_spline, y_spline, z_spline = splev(u_fine, tck)

# Plot noisy points and fitted spline
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z, color='red', label='Noisy Data')
ax.plot(x_spline, y_spline, z_spline, color='blue', label='Fitted Curve')
ax.legend()
plt.show()
