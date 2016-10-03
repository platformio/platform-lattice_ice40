# -*- coding: utf-8 -*-
# Copyright 2014-present PlatformIO <contact@platformio.org>
# Copyright 2016 Juan González <juan@iearobotics.com>
#                Jesús Arroyo Torrens <jesus.jkhlg@gmail.com>
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
"""

import os
from os.path import join
from platform import system

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Builder, Default,
                          DefaultEnvironment, Environment, Exit, GetOption,
                          Glob)

env = DefaultEnvironment()
env.Replace(PROGNAME="hardware")
env.Append(SIMULNAME="simulation")

# -- Target name for synthesis
TARGET = join(env['BUILD_DIR'], env['PROGNAME'])

# -- Resources paths
pioPlatform = env.PioPlatform()
IVL_PATH = join(
    pioPlatform.get_package_dir('toolchain-iverilog'), 'lib', 'ivl')
VLIB_PATH = join(
    pioPlatform.get_package_dir('toolchain-iverilog'), 'vlib', 'system.v')

isWindows = 'Windows' != system()
VVP_PATH = '-M {0}'.format(IVL_PATH) if isWindows else ''
IVER_PATH = '-B {0}'.format(IVL_PATH) if isWindows else ''

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
        print "---> ERROR: NO testbench found for simulation"
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
    print "---> ERROR: no .pcf file found"
    Exit(1)

# -- Debug
print "PCF: %s" % PCF

# -- Builder 1 (.v --> .blif)
synth = Builder(
    action='yosys -p \"synth_ice40 -blif $TARGET\" $SOURCES',
    suffix='.blif',
    src_suffix='.v')

# -- Builder 2 (.blif --> .asc)
pnr = Builder(
    action='arachne-pnr -d {0} -P {1} -p {2} -o $TARGET $SOURCE'.format(
        env.BoardConfig().get('build.size', '1k'),
        env.BoardConfig().get('build.pack', 'tq144'),
        PCF
    ),
    suffix='.asc',
    src_suffix='.blif')

# -- Builder 3 (.asc --> .bin)
bitstream = Builder(
    action='icepack $SOURCE $TARGET',
    suffix='.bin',
    src_suffix='.asc')

# -- Builder 4 (.asc --> .rpt)
# NOTE: current icetime requires a fixed PREFIX during compilation
#       update on toolchain-icestorm 1.10.0
# https://github.com/cliffordwolf/icestorm/issues/57
time_rpt = Builder(
    action='icetime -d {0}{1} -P {2} -mtr $TARGET $SOURCE'.format(
        env.BoardConfig().get('build.type', 'hx'),
        env.BoardConfig().get('build.size', '1k'),
        env.BoardConfig().get('build.pack', 'tq144')
    ),
    suffix='.rpt',
    src_suffix='.asc')


env.Append(BUILDERS={
    'Synth': synth, 'PnR': pnr, 'Bin': bitstream, 'Time': time_rpt})

blif = env.Synth(TARGET, [src_synth])
asc = env.PnR(TARGET, [blif, PCF])
binf = env.Bin(TARGET, asc)

upload = env.Alias('upload', binf, 'iceprog $SOURCE')
AlwaysBuild(upload)

# -- Target for calculating the time (.rpt)
rpt = env.Time(asc)
t = env.Alias('time', rpt)
AlwaysBuild(t)

# -- Icarus Verilog builders

iverilog = Builder(
    action='iverilog {0} -o $TARGET {1} -D VCD_OUTPUT={2} $SOURCES'.format(
        IVER_PATH, VLIB_PATH, TARGET_SIM),
   suffix='.out',
   src_suffix='.v')

# NOTE: output file name is defined in the iverilog call using VCD_OUTPUT macro
vcd = Builder(
    action='vvp {0} $SOURCE'.format(
        VVP_PATH),
    suffix='.vcd',
    src_suffix='.out')

# -------------------- Simulation ------------------
env.Append(BUILDERS={'IVerilog': iverilog, 'VCD': vcd})

out = env.IVerilog(TARGET_SIM, src_sim)
vcd_file = env.VCD(out)

waves = env.Alias('sim', vcd_file, 'gtkwave {0} {1}.gtkw'.format(
    vcd_file[0], join(env['PROJECTSRC_DIR'], SIMULNAME)))
AlwaysBuild(waves)

Default([binf])

# -- These is for cleaning the files generated using the alias targets
if GetOption('clean'):
    env.Default([t, sout, vcd_file])
