#!/usr/bin/env python3
from PySpice.Spice.NgSpice.Shared import NgSpiceShared
import matplotlib.pyplot as plt
import sys
import time
import numpy as np

# 1. Initialize the ngspice shared library
ngspice = NgSpiceShared.new_instance()
netlist_file = 'opamp_netlist_fixed.sp' if len(sys.argv) < 2 else sys.argv[1]
print(f'Using netlist file {netlist_file}')
with open(netlist_file, 'r') as f:
    file_content = f.read()

# 2. Load your file directly (this skips the buggy PySpice parser)
start = time.time()
try:
    ngspice.load_circuit(file_content)
except Exception as e:
    print(f"load_circuit: Handled ngspice status message entry safely: {e}")
    print(f'load_circuit: stdout: {ngspice._error_in_stdout}', '...')
    print(f'load_circuit: stderr: {ngspice._error_in_stderr}: {ngspice.stderr}', '...')
end = time.time()
print(f'simulation load_circuit took {(end-start):.2f}s.')

# 3. Run the simulation
start = time.time()
try:
    ngspice.run()
except Exception as e:
    print(f"run: Handled ngspice status message entry safely: {e}")
    print(f'run: stdout: {ngspice._error_in_stdout}', '...')
    print(f'run: stderr: {ngspice._error_in_stderr}: {ngspice.stderr}', '...')
end = time.time()
print(f'simulation run took {(end-start):.2f}s.')

# 4. Access your data (e.g., from the last simulation run)
# 1. Get the time vector (the X-axis)
# In ngspice, the time vector is usually named 'time' or 'v(time)'
# When ngspice executes multiple analyses, it saves them into distinct "plots"
print(f"Available memory plots: {ngspice.plot_names}, last plot {ngspice.last_plot}")

run_ids = [2, 1]
for run_id in run_ids:
    print(f'Processing run id {run_id}...')
    try:
        ngspice.exec_command(f'destroy tran{run_id}.fourier11')
    except Exception as e:
        # If it doesn't exist, Python safely skips the error and proceeds
        print("fourier11 not found or already deleted:", e)

    # Print Op data
    op_data = ngspice.plot(ngspice.last_plot, f'op{run_id}')
    print(f'Run {run_id} op data: {op_data}')
    # Access the AC data block (typically named 'ac1')
    ac_plot = ngspice.plot(ngspice.last_plot, f'ac{run_id}')
    print(f'Getting data from {ac_plot["frequency"]._name} and {ac_plot["vout"]._name}:')
    frequencies = ac_plot['frequency']._data
    v_complex = ac_plot['vout']._data
    print(f'frequencies shape {frequencies.shape}, frequencies type {frequencies.dtype}, v_complex shape {v_complex.shape}, v_complex data type {v_complex.dtype}')
    magnitude_db = 20 * np.log10(np.abs(v_complex))
    plt.figure(figsize=(12, 5))
    # 4. Create the plot
    plt.subplot(1, 3, 1)
    plt.semilogx(np.abs(frequencies), magnitude_db, label='Vout Magnitude (dB)', color='red')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Voltage (V)')
    plt.title('Op-Amp AC Magnitude Response')
    plt.grid(True, which='both')
    plt.legend()

    plt.subplot(1, 3, 2)
    plt.semilogx(np.abs(frequencies), np.angle(v_complex, deg=True), label='Vout Phase (deg)', color='green')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Phase (deg)')
    plt.title('Op-Amp AC Phase Response')
    plt.grid(True, which='both')
    plt.legend()
    # Bug in PySpice for getting transient data for tran1: 
    # Error: vector tran1.fourier11 is multidimensional!
    # This is not yet handled
    # Segmentation fault: 11
    if run_id != 1:
        tran_plot = ngspice.plot(ngspice.last_plot, f'tran{run_id}')
        print(f'Getting data from {tran_plot["time"]._name} and {tran_plot["vout"]._name}:')
        time_data = tran_plot['time']._data
        # 2. Get your output voltage (the Y-axis)
        vout_data = tran_plot['vout']._data
        print(f'time_data shape {time_data.shape}, time_data type {time_data.dtype}, vout_data shape {vout_data.shape}, vout_data type {vout_data.dtype}')
        # 3. Create the plot
        plt.subplot(1, 3, 3)
        plt.plot(time_data, vout_data, label='Vout', color='blue')
        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (V)')
        plt.title('Op-Amp Transient Response')
        plt.grid(True)
        plt.legend()
    else:
        plt.subplot(1, 3, 3)
        plt.semilogx(np.abs(frequencies), np.angle(v_complex, deg=True), label='Vout Phase (deg)', color='blue')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Phase (deg)')
        plt.title('Op-Amp AC Phase Response')
        plt.grid(True, which='both')
        plt.legend()
    plt.tight_layout()
    plt.show()
