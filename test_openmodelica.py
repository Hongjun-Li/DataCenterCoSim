from pyfmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt

model = load_fmu("InputDriven.fmu", kind="CS")


start_time = 0.0
stop_time = 10.0
step_size = 0.1
n_steps = int((stop_time - start_time) / step_size)

model.initialize(start_time=start_time, stop_time=stop_time)

time_log = []
u_log = []
y_log = []

t = start_time

for i in range(n_steps):
    
    u_val = np.sin(t)
    model.set("u", u_val)
    model.do_step(current_t=t, step_size=step_size)

    y_val = model.get("y")

    time_log.append(t)
    u_log.append(u_val)
    y_log.append(y_val)

    t += step_size

model.terminate()

plt.figure(figsize=(10, 5))
plt.plot(time_log, u_log, '--', label="u (input)")
plt.plot(time_log, y_log, label="y (output)")
plt.xlabel("Time (s)")
plt.ylabel("Value")
plt.title("InputDriven.fmu Simulation with pyfmi")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

