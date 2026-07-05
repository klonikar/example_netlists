#!/usr/bin/env python3
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from PySpice.Spice.NgSpice.Shared import NgSpiceShared

# 1. Initialize the low-level ngspice shared library instance
netlist_file = 'opamp_netlist_ngspice.sp' if len(sys.argv) < 2 else sys.argv[1]
print(f'Using netlist file {netlist_file}')

with open(netlist_file, 'r') as f:
    file_content = f.read()

ngspice = NgSpiceShared.new_instance()

# 2. Load the raw text string directly into ngspice's native parser
print('Loading circuit string natively into ngspice...')
ngspice.load_circuit(file_content)
print('Loaded circuit successfully')
simulations_to_execute = ['op', 'tran 1n 10m', 'ac dec 10 10 100meg']
for sim_cmd in simulations_to_execute:
    start = time.time()
    try:
        # 2. Setup and run the independent Operating Point first
        ngspice._error_in_stderr = False
        ngspice._error_in_stdout = False
        print('Cleared false-positive error flags.')
        ngspice.clear_output()
        ngspice.exec_command(sim_cmd)
        print('Simulations op completed successfully.')
    except Exception as e:
        print(f"Simulation Error Caught: {e}")
        print(f'{sim_cmd}: stdout: {ngspice._error_in_stdout}', '...')
        print(f'{sim_cmd}: stderr: {ngspice._error_in_stderr}: {ngspice.stderr}', '...')
    end = time.time()
    print(f'simulation {sim_cmd} took {(end-start):.2f}s.')

# --- 4. DATA EXTRACTION FROM NGSPACE MEMORY PLOTS ---
# When ngspice executes multiple analyses, it saves them into distinct "plots"
print(f"Available memory plots: {ngspice.plot_names}, last plot {ngspice.last_plot}")

# Access the Transient data block (typically named 'tran1')
tran_plot = ngspice.plot(ngspice.last_plot, 'tran1')
print(f'Getting data from {tran_plot["time"]._name} and {tran_plot["vout"]._name}:')
time_data = np.array(tran_plot['time']._data)
vout_data = np.array(tran_plot['vout']._data)
print(f'time_data shape {time_data.shape}, time_data type {time_data.dtype}, vout_data shape {vout_data.shape}, vout_data type {vout_data.dtype}')

# Access the AC data block (typically named 'ac1')
ac_plot = ngspice.plot(ngspice.last_plot, 'ac1')
print(f'Getting data from {ac_plot["frequency"]._name} and {ac_plot["vout"]._name}:')
frequencies = np.array(ac_plot['frequency']._data)
v_complex = np.array(ac_plot['vout']._data)
print(f'frequencies shape {frequencies.shape}, frequencies type {frequencies.dtype}, v_complex shape {v_complex.shape}, v_complex data type {v_complex.dtype}')

# --- 5. PERFORMANCE METRIC CALCULATIONS ---
VDD = 1.8
v30 = 0.3 * VDD   # 0.54V 
v70 = 0.7 * VDD   # 1.26V 
v99 = 0.99 * VDD  # 1.782V 

# Compute Overshoot
max_voltage = np.max(vout_data)
print(f'max voltage: {max_voltage}.')
overshoot = max_voltage - VDD
overshoot_percentage = (overshoot / VDD) * 100
print(f"\n--- Analysis Performance Metrics ---")
print(f"Overshoot: {overshoot_percentage:.2f}%")

# Compute Slew Rate (Rise)
try:
    t30_r = time_data[np.where(vout_data >= v30)[0][0]]
    t70_r = time_data[np.where(vout_data >= v70)[0][0]]
    slew_rise = (v70 - v30) / (t70_r - t30_r)  # V/s
    print(f"Slew Rate Rise: {slew_rise / 1e6:.2f} V/µs")
except IndexError:
    print("Slew Rate Rise: Failed to compute (Output did not cross thresholds).")

# Compute 1% Settling Time
error_band_low = VDD * 0.99
outside_band_indices = np.where(vout_data < error_band_low)[0]
if len(outside_band_indices) > 0:
    settling_time = time_data[outside_band_indices[-1]]
    print(f"1% Settling Time: {settling_time * 1e6:.2f} µs")

# --- 6. PLOTTING THE RESULTS ---
plt.figure(figsize=(12, 5))
# Plot 1: AC Analysis (Bode Magnitude Plot)
magnitude_db = 20 * np.log10(np.abs(v_complex))
plt.subplot(1, 3, 1)
plt.semilogx(np.abs(frequencies), magnitude_db, label='Gain (dB)', color='red')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude (dB)')
plt.title('Op-Amp AC Magnitude Response')
plt.grid(True, which="both")
plt.legend()

plt.subplot(1, 3, 2)
plt.semilogx(np.abs(frequencies), np.angle(v_complex, deg=True), label='Vout Phase (deg)', color='green')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Phase (deg)')
plt.title('Op-Amp AC Phase Response')
plt.grid(True, which='both')
plt.legend()

# Plot 2: Transient Analysis
plt.subplot(1, 3, 3)
plt.plot(time_data * 1e3, vout_data, label='Vout', color='blue')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.title('Op-Amp Transient Response')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
