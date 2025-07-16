from pyfmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt

# Simulation setup
model_name = 'co'
days = 1
steps_per_hour = 24 * 60
total_steps = days * steps_per_hour
t_end = days * 24 * 60 * 60  # seconds
step_size = t_end / total_steps

# Load FMU
model = load_fmu(model_name + '.fmu')
opts = model.simulate_options()
opts['ncp'] = total_steps
opts['initialize'] = False

# Time array
time_vector = np.linspace(0, t_end, total_steps)
time_hours = time_vector / 3600  # convert to hours

# -------------------
# Input: Tfmu (cooling setpoint)
# Default 15°C, decrease by 2°C between 14:00 and 16:00
Tfmu_values = np.full(total_steps, 15.0)

for day in range(days):
    start_hour = 14 + 24 * day
    end_hour = 16 + 24 * day
    condition = (time_hours >= start_hour) & (time_hours <= end_hour)
    Tfmu_values[condition] -= 2.0

# Input: AFfmu (airflow rate), constant
AFfmu_values = np.full(total_steps, 17.0)
# -------------------

# Initialize model
sim_time = 0
model.initialize(start_time=sim_time, stop_time=t_end)

# Output arrays
Tmain_log = np.zeros(total_steps)
Tsub_log = np.zeros(total_steps)
Tret_log = np.zeros(total_steps)
Tsup1_log = np.zeros(total_steps)
Tsup2_log = np.zeros(total_steps)
Q_log= np.zeros(total_steps)

Tfmu_check = np.zeros(total_steps)
AFfmu_check = np.zeros(total_steps)

# Simulation loop
for i in range(total_steps):
    model.set('Tfmu', Tfmu_values[i])
    model.set('AFfmu', AFfmu_values[i])
    model.do_step(current_t=sim_time, step_size=step_size)

    Tfmu_check[i] = model.get('Tfmu')
    AFfmu_check[i] = model.get('AFfmu')

    Tmain_log[i] = model.get('Tmain')
    Tsub_log[i] = model.get('Tsub')
    Tret_log[i] = model.get('Tret')
    Tsup1_log[i] = model.get('Tsup1')
    Tsup2_log[i] = model.get('Tsup2')
    Q_log[i] = model.get('Q')


    sim_time += step_size


import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharex=True)
# Plotting temperatures
ax1.plot(time_hours, Tmain_log, label='Tmain (MAIN ZONE)')
ax1.plot(time_hours, Tsub_log, label='Tsub (SUB ZONE)')
ax1.plot(time_hours, Tret_log, label='Tret (PLENUM-1)')
ax1.plot(time_hours, Tsup1_log, label='Tsup1 (SUP-PLENUM-1)')
ax1.plot(time_hours, Tsup2_log, label='Tsup2 (SUP-PLENUM-2)')

ax1.set_xlabel('Time (hours)')
ax1.set_ylabel('Temperature (°C)')
ax1.set_title('Zone Air Temperatures')
ax1.grid(True)
ax1.legend()

# plotting heat transfer
ax2.plot(time_hours, Q_log, label='Q (Heat Flow)', color='red')
ax2.set_xlabel('Time (hours)')
ax2.set_ylabel('Q (W)')
ax2.set_title('Heat Transfer Q to FMU')
ax2.grid(True)
ax2.legend()

plt.tight_layout()
plt.show()
