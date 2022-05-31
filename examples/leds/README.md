How to build PlatformIO based project
=====================================

1. [Install PlatformIO Core](https://docs.platformio.org/page/core.html)
2. Download [development platform with examples](https://github.com/platformio/platform-lattice_ice40/archive/develop.zip)
3. Extract ZIP archive
4. Run these commands:

```shell
# Change directory to example
$ cd platform-lattice_ice40/examples/leds

# Build project
$ pio run

# Verify project
$ pio run --target verify

# Launch simulation
$ pio run --target sim

# Launch time analysis
$ pio run --target time

# Upload bitstream into the FPGA
$ pio run --target upload

# Clean build files
$ pio run --target clean
```

NOTE: [GTKwave](http://gtkwave.sourceforge.net) is required for simulation
