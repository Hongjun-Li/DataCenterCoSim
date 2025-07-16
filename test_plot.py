from pyfmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt

# 加载 FMU
model = load_fmu("IntegratedPrimaryLoadSideEconomizer.fmu")

# 仿真设置
start_time = 0.0
stop_time = 36000.0
n_points = 1000
time_points = np.linspace(start_time, stop_time, n_points)
Qroo_input = np.ones(n_points) * 100000
input_object = ("Qroo", np.column_stack((time_points, Qroo_input)))

# 仿真运行
result = model.simulate(
    start_time=start_time,
    final_time=stop_time,
    input=input_object
)

# 提取变量
Tret = result['Tsup'] - 273.15  # 转为摄氏度（可选）
AF = result['AF']
time = result['time']

# 创建两个子图（并排）
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), sharex=True)

# 左图：温度
ax1.plot(time, Tret, color='tab:red')
ax1.set_xlabel("Time [s]")
ax1.set_ylabel("Tsup [°C]")
ax1.set_title("Supply Temp (Tsup)")
ax1.grid(True)

# 右图：风量
ax2.plot(time, AF, color='tab:blue')
ax2.set_xlabel("Time [s]")
ax2.set_ylabel("Air Flow [kg/s]")
ax2.set_title("Air Flow Rate (AF)")
ax2.grid(True)

# 布局调整
plt.tight_layout()
plt.show()
