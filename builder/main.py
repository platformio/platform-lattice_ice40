# Copyright 2014-present PlatformIO <contact@platformio.org>
# Copyright 2016 Juan Gonzalez <juan@iearobotics.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    Build script for lattice ice40 FPGAs
    latticeice40-builder.py
"""

import os
from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Builder, Default,
                          DefaultEnvironment, Environment, Exit, GetOption,
                          Glob)

env = DefaultEnvironment()
env.Replace(PROGNAME="hardware")
env.Append(SIMULNAME="simulation")

# -- Target name for synthesis
TARGET = join(env['BUILD_DIR'], env['PROGNAME'])

# -- Target name for simulation
# TARGET_SIM = join(env['PROJECT_DIR'], env['SIMULNAME'])

# -- Get a list of all the verilog files in the src folfer, in ASCII, with
# -- the full path. All these files are used for the simulation
v_nodes = Glob(join(env['PROJECTSRC_DIR'], '*.v'))
src_sim = [str(f) for f in v_nodes]

# --------- Get the Testbench file (there should be only 1)
# -- Create a list with all the files finished in _tb.v. It should contain
# -- the test bench
list_tb = [f for f in src_sim if f[-5:].upper() == "_TB.V"]

if len(list_tb) > 1:
    print "---> WARNING: More than one testbenches used"

# -- Error checking
try:
    testbench = list_tb[0]

# -- there is no testbench
except IndexError:
    testbench = None

if 'sim' in COMMAND_LINE_TARGETS:
    if testbench is None:
        print "ERROR!!! NO testbench found for simulation"
        Exit(1)

    # -- Simulation name
    testbench_file = os.path.split(testbench)[-1]
    SIMULNAME, ext = os.path.splitext(testbench_file)
else:
    SIMULNAME = ''


TARGET_SIM = join(env.subst('$BUILD_DIR'), SIMULNAME)

# -------- Get the synthesis files.  They are ALL the files except the
# -------- testbench
src_synth = [f for f in src_sim if f not in list_tb]

# -- For debugging
print "Testbench: %s" % testbench

# -- Get the PCF file
src_dir = env.subst('$PROJECTSRC_DIR')
PCFs = join(src_dir, '*.pcf')
PCF_list = Glob(PCFs)

try:
    PCF = PCF_list[0]
except IndexError:
    print "\n--------> ERROR: no .pcf file found <----------\n"
    Exit(2)

# -- Debug
print "----> PCF Found: %s" % PCF

# -- Builder 1 (.v --> .blif)
synth = Builder(
    action='yosys -p \"synth_ice40 -blif %s.blif\" $SOURCES' % TARGET,
    suffix='.blif',
    src_suffix='.v')

# -- Builder 2 (.blif --> .asc)
pnr = Builder(
    action='arachne-pnr -d 1k -o $TARGET -p %s $SOURCE' % PCF,
    suffix='.asc',
    src_suffix='.blif')

# -- Builder 3 (.asc --> .bin)
bitstream = Builder(
    action='icepack $SOURCE $TARGET',
    suffix='.bin',
    src_suffix='.asc')

# -- Builder 4 (.asc --> .rpt)
time_rpt = Builder(
    action='icetime -mtr $TARGET $SOURCE',
    suffix='.rpt',
    src_suffix='.asc')

env.Append(BUILDERS={
    'Synth': synth, 'PnR': pnr, 'Bin': bitstream, 'Time': time_rpt})

blif = env.Synth(TARGET, [src_synth])
asc = env.PnR(TARGET, [blif, PCF])
binf = env.Bin(TARGET, asc)

upload = env.Alias('upload', binf, 'iceprog ' + ' $SOURCE')
AlwaysBuild(upload)

# -- Target for calculating the time (.rpt)
# rpt = env.Time(asc)
t = env.Alias('time', env.Time('time.rpt', asc))

# -------------------- Simulation ------------------
# -- Constructor para generar simulacion: icarus Verilog
iverilog = Builder(action='iverilog -o $TARGET $SOURCES ',
                   suffix='.out',
                   src_suffix='.v')

vcd = Builder(action=' $SOURCE',
              suffix='.vcd', src_suffix='.out')

simenv = Environment(BUILDERS={'IVerilog': iverilog, 'VCD': vcd},
                     ENV=os.environ)

out = simenv.IVerilog(TARGET_SIM, src_sim)
vcd_file = simenv.VCD(SIMULNAME, out)

waves = simenv.Alias('sim', vcd_file, 'gtkwave ' +
                     join(env['PROJECT_DIR'], "%s " % vcd_file[0]) +
                     join(env['PROJECTSRC_DIR'], SIMULNAME) +
                     '.gtkw')
AlwaysBuild(waves)

Default([binf])

# -- These is for cleaning the files generated using the alias targets
if GetOption('clean'):
    env.Default([t])
    simenv.Default([out, vcd_file])
