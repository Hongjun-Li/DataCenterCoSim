from pyfmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt

model = load_fmu("IntegratedPrimaryLoadSideEconomizer.fmu")

start_time = 0.0
stop_time = 36000.0
n_points = 1000
time_points = np.linspace(start_time, stop_time, n_points)
Qroo_input = np.ones(n_points) * 500000
input_object = ("Qroo", np.column_stack((time_points, Qroo_input)))

result = model.simulate(
    start_time=start_time,
    final_time=stop_time,
    input=input_object
)

Tsup = result['Tsup'] - 273.15  
AF = result['AF']
time = result['time']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), sharex=True)

ax1.plot(time, Tsup, color='tab:red')
ax1.set_xlabel("Time [s]")
ax1.set_ylabel("Tsup [°C]")
ax1.set_title("Supply Temp (Tsup)")
ax1.grid(True)

ax2.plot(time, AF/10, color='tab:blue')
ax2.set_xlabel("Time [s]")
ax2.set_ylabel("Air Flow [kg/s]")
ax2.set_title("Air Flow Rate (AF)")
ax2.grid(True)

plt.tight_layout()
plt.show()
