from pyfmi import load_fmu
model = load_fmu("IntegratedPrimaryLoadSideEconomizer.fmu")
model.setup_experiment(start_time=0.0)

result = model.simulate(start_time=0.0, final_time=100.0)
print("✅ 仿真成功")
