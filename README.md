# Lattice iCE40: development platform for [PlatformIO](https://platformio.org)

[![Build Status](https://github.com/platformio/platform-lattice_ice40/workflows/Examples/badge.svg)](https://github.com/platformio/platform-lattice_ice40/actions)


Lattice iCE40 are the first FPGAs fully usable by open source tools.

* [Home](https://registry.platformio.org/platforms/platformio/lattice_ice40) (home page in the PlatformIO Registry)
* [Documentation](https://docs.platformio.org/page/platforms/lattice_ice40.html) (advanced usage, packages, boards, frameworks, etc.)

# Usage

1. [Install PlatformIO](https://platformio.org)
2. Create PlatformIO project and configure a platform option in [platformio.ini](https://docs.platformio.org/page/projectconf.html) file:

## Stable version

```ini
[env:stable]
platform = lattice_ice40
board = ...
...
```

## Development version

```ini
[env:development]
platform = https://github.com/platformio/platform-lattice_ice40.git
board = ...
...
```

# Configuration

Please navigate to [documentation](https://docs.platformio.org/page/platforms/lattice_ice40.html).


# Credits

* [Apio](https://github.com/FPGAwars/apio)
* [Icestorm](http://www.clifford.at/icestorm/)
* [Icarus Verilog](http://iverilog.icarus.com/)
