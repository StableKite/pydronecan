DroneCAN v1 stack in Python  [a fork of UAVCAN v0.9]
==========================


Python implementation of the [DroneCAN v1 protocol stack](http://dronecan.github.io).

DroneCAN is a lightweight protocol designed for reliable communication in aerospace and robotic applications via CAN bus.

## Documentation

* [DroneCAN v1 website](http://dronecan.github.io)
* [Pydronecan documentation and tutorials](http://dronecan.github.io/Implementations/Pydronecan/)

## Installation

Compatible Python versions are 2.7 and 3.3 and newer.
If the library is used with Python 3, which is recommended, it does not require any additional dependencies.
If Python 2.7 is used, additional dependencies are needed - refer to `setup.py` for more info.

```bash
pip install dronecan
```

## Development

### Automatic deployment to PyPI

In order to deploy to PyPI via CI, do this:

1. Update the version number in `version.py`, e.g. `1.0.0`, and commit before proceeding.
2. Create a new tag with the same version number, e.g. `git tag -a 1.0.0 -m "My release 1.0.0"`
3. Push to master.

### Code style

Please follow the existing coding styles.

## History

Much of the development of this tool is based upon original work by
Pavel Kirienko and others from the UAVCAN Development Team. See
https://github.com/UAVCAN/pyuavcan/tree/legacy-v0 for contributors.


StableKite PEP 561 contract scope
--------------------------------
This fork describes the actual Root-facing DATATYPES/TYPENAMES registries and
the transport and DSDL parser APIs in five covered modules. Their stubs pass
current strict mypy/Pyright and runtime stubtest without an allowlist. Other
node/driver/application modules remain unannotated; whole-package strict
completeness or generated field-specific DSDL namespace typing is not claimed.
Dynamic field values use finite scalar/value/iterable unions, never Any.

A raw CompoundType factory initially returns None until load_dsdl binds it.
The callable result is therefore CompoundValue | None; consumers must check
it before unpacking. Transfer.payload preserves its actual serialized
bytearray / decoded CompoundValue / None states. Empty Frame.transfer_key
contains a None transfer ID. No runtime codec behavior has been changed.

Ordinary Git builds include the exact 147 DSDL files bundled with upstream
1.0.27, from DSDL commit 04e0e818b06c180eb1720fcdf16484d0f12895ee.
SOURCE_DSDL.json records their original source and hashes; builds require no
external sibling DSDL checkout or Windows symlink privileges. All 58 original
tests are preserved, and the native contract probe compares 145 type
signatures, 124 registry entries, and 346 real codec cases to that baseline.
