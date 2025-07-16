from pyfmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# 1. Load both FMUs
# ----------------------------
model1 = load_fmu("IntegratedPrimaryLoadSideEconomizer.fmu")
model2 = load_fmu("co.fmu")

# ----------------------------
# 2. Simulation settings
# ----------------------------
start_time = 0.0
stop_time = 86400.0  # 24 hours
step_size = 60.0  # seconds
n_steps = int((stop_time - start_time) / step_size)

# ----------------------------
# 3. Initialize models
# ----------------------------
# Initialize both FMUs
model1.setup_experiment(start_time=start_time, stop_time=stop_time)
model1.initialize(start_time=start_time, stop_time=stop_time)

model2.setup_experiment(start_time=start_time, stop_time=stop_time)
model2.initialize(start_time=start_time, stop_time=stop_time)

# ----------------------------
# 4. Preallocate arrays for logging
# ----------------------------
time_log = np.zeros(n_steps)
Tmain_log = np.zeros(n_steps)
Tsub_log = np.zeros(n_steps)
Q_log = np.zeros(n_steps)

Tsup1_log = np.zeros(n_steps)
Tsup2_log = np.zeros(n_steps)
Tret_log = np.zeros(n_steps)

Tfmu_log = np.zeros(n_steps)
AFfmu_log = np.zeros(n_steps)

# ----------------------------
# 5. Simulation loop (co-simulation coupling)
# ----------------------------
sim_time = start_time

for i in range(n_steps):
    # (a) FMU1 do_step
    # Input to FMU1: Qroo (here constant)
    if i == 0:
        Qroo_value = 160000
    else:
        Qroo_value = Q_log[i - 1]
    model1.set('Qroo', Qroo_value)

    model1.do_step(current_t=sim_time, step_size=step_size)

    # Read FMU1 outputs after this step
    Tfmu = model1.get('Tsup') - 273.15
    AFfmu = model1.get('AF')

    Tfmu_log[i] = Tfmu
    AFfmu_log[i] = AFfmu

    # (b) FMU2 do_step using FMU1 outputs
    model2.set('Tfmu', Tfmu)
    model2.set('AFfmu', AFfmu)

    model2.do_step(current_t=sim_time, step_size=step_size)

    # Record FMU2 outputs
    time_log[i] = sim_time / 3600.0  # hours
    Tmain_log[i] = model2.get('Tmain')
    Tsub_log[i] = model2.get('Tsub')
    Tret_log[i] = model2.get('Tret')
    Tsup1_log[i] = model2.get('Tsup1')
    Tsup2_log[i] = model2.get('Tsup2')
    Q_log[i] = model2.get('Q')

    # Advance time
    sim_time += step_size

# ----------------------------
# 6. Plot results
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
