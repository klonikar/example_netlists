# example_netlists
Simple netlists and a PySpice based tool to simulate them
## Install PySpice
`pip install pyspice`
## Build and Install ngspice
Sometimes, the usual instructions to install ngspice with it's shared library do not work, especially on Mac. Follow instructions here to build and install it:
https://github.com/danchitnis/ngspice-sf-mirror/blob/ngspice-44/INSTALL

Check that PySpice and ngspice are correctly installed: `python -c "from PySpice.Spice.NgSpice.Shared import NgSpiceShared"`

## Install open source PDKs
```
pip install volare
volare ls-remote --pdk sky130
volare fetch --pdk sky130 c6d73a35f524070e85faff4a6a9eef49553ebc2b # The latest one
volare ls-remote --pdk gf180mcu
volare fetch --pdk gf180mcu 0fe599b2afb6708d281543108caf8310912f54af
volare fetch --pdk gf180mcu c6d73a35f524070e85faff4a6a9eef49553ebc2b # The latest one
volare ls --pdk gf180mcu
volare ls --pdk sky130
volare enable --pdk gf180mcu c6d73a35f524070e85faff4a6a9eef49553ebc2b
volare enable --pdk sky130 c6d73a35f524070e85faff4a6a9eef49553ebc2b
```
## Optional: Locally build PDK
### Install magic first: Need to install VLSI Magic.
### Follow this guide: https://github.com/RTimothyEdwards/magic/blob/master/INSTALL_MacOS.md
```
#brew install --force xquartz tcl-tk@8 cairo libglu jpeg gnu-sed
brew install --force xquartz tcl-tk cairo libglu jpeg gnu-sed
git clone https://github.com/RTimothyEdwards/magic.git
cd magic
./configure --with-tcl=/usr/local/opt/tcl-tk/lib --with-tk=/usr/local/opt/tcl-tk/lib
# edit defs.mak and change /usr/bin/sed to /usr/local/opt/gnu-sed/libexec/gnubin
make
sudo make install
# Go for lunch, a walk... This takes a long time and large disk space
volare build --pdk gf180mcu 0fe599b2afb6708d281543108caf8310912f54af
```

# Test
`./simulate_netlist.py opamp_netlist_ngspice.sp`

At the moment, only this netlist works. This utility requires that you put only the circuit definition in the netlist: No .op, .ac, .tran, and run in .control block. The python simulator script uses python function `exec_command` to carry out different types of simulations. This means python code has full control on what to execute and perform analysis of results using advanced python libraries.

# Test files in orig_circuit_defs 
`./simulate_netlist.py opamp_netlist_ngspice.sp`

At the moment, only this netlist works. The netlist can have .op, .ac, .tran, and run in .control block. When the python simulator script calls `load_circuit`, these statements execute. Additionally, `run()` function executes any queued simulation tasks. This means python code does not have any control on what to execute and perform analysis of results using advanced python libraries.
