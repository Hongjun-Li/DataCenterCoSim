from pyfmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# 1. Run the first FMU model
# ----------------------------

# Load first FMU
model1 = load_fmu("IntegratedPrimaryLoadSideEconomizer.fmu")

# Simulation settings: 1 day, 1 point per minute
start_time = 0.0
stop_time = 86400.0  # 24 hours in seconds
step_size = 60.0  # seconds
n_points = int((stop_time - start_time) / step_size) + 1
time_points = np.linspace(start_time, stop_time, n_points)

# Constant Qroo input
Qroo_input = np.ones(n_points) * 500000
input_object = ("Qroo", np.column_stack((time_points, Qroo_input)))

# Simulation options
opts1 = model1.simulate_options()
opts1['ncp'] = n_points - 1  # control points = number of time steps - 1

# Run simulation
result1 = model1.simulate(
    start_time=start_time,
    final_time=stop_time,
    input=input_object,
    options=opts1
)

# Extract results
Tfmu_values = result1['Tsup'] - 273.15  # °C
AFfmu_values = result1['AF']
time_sim1 = result1['time']

# ----------------------------
# 2. Drive the second FMU model
# ----------------------------

# Load second FMU (e.g., EnergyPlus)
model2 = load_fmu("co.fmu")

# Total steps match first simulation
total_steps = len(Tfmu_values)

# Initialize model2
model2_opts = model2.simulate_options()
model2_opts['ncp'] = total_steps
model2_opts['initialize'] = False
model2.initialize(start_time=0.0, stop_time=stop_time)

# Preallocate output arrays
time_log = np.zeros(total_steps)
Tmain_log = np.zeros(total_steps)
Tsub_log = np.zeros(total_steps)
Tret_log = np.zeros(total_steps)
Tsup1_log = np.zeros(total_steps)
Tsup2_log = np.zeros(total_steps)
Q_log = np.zeros(total_steps)

# Simulation loop
sim_time = 0.0
for i in range(total_steps):
    model2.set('Tfmu', Tfmu_values[i])
    model2.set('AFfmu', AFfmu_values[i])
    
    model2.do_step(current_t=sim_time, step_size=step_size)

    time_log[i] = sim_time / 3600.0  # hours
    Tmain_log[i] = model2.get('Tmain')
    Tsub_log[i] = model2.get('Tsub')
    Tret_log[i] = model2.get('Tret')
    Tsup1_log[i] = model2.get('Tsup1')
    Tsup2_log[i] = model2.get('Tsup2')
    Q_log[i] = model2.get('Q')

    sim_time += step_size

# ----------------------------
# 3. Plot Results
# ----------------------------

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharex=True)


# Temperatures
ax1.plot(time_log, Tmain_log, label='Tmain (MAIN ZONE)')
ax1.plot(time_log, Tsub_log, label='Tsub (SUB ZONE)')
ax1.plot(time_log, Tret_log, label='Tret (PLENUM-1)')
ax1.plot(time_log, Tsup1_log, label='Tsup1 (SUP-PLENUM-1)')
ax1.plot(time_log, Tsup2_log, label='Tsup2 (SUP-PLENUM-2)')
ax1.set_xlabel('Time (hours)')
ax1.set_ylabel('Temperature (°C)')
ax1.set_title('Zone Air Temperatures')
ax1.grid(True)
ax1.legend()

# Heat transfer
ax2.plot(time_log, Q_log, label='Q (Heat Flow)', color='red')
ax2.set_xlabel('Time (hours)')
ax2.set_ylabel('Q (W)')
ax2.set_title('Heat Transfer to FMU')
ax2.grid(True)
ax2.legend()

plt.tight_layout()
plt.show()
