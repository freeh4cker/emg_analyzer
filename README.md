# EMG Analyzer
[![Build Status](https://travis-ci.org/freeh4cker/emg_analyzer.svg?branch=master)](https://travis-ci.org/freeh4cker/emg_analyzer)
[![Coverage Status](https://coveralls.io/repos/github/freeh4cker/emg_analyzer/badge.svg?branch=master)](https://coveralls.io/github/freeh4cker/emg_analyzer?branch=master)


Is a tool set to help to analyze ElectroMyoGraphy recorded via smart analyzer.
For now it is able to normalyze The voltage from an Electromyography recorded file (.emt file)
and produce a new .emt file with the normalized voltage, this new file can be open in smart analyzer.

## Installation

*emg_analyzer* is not yet registered on PyPI so you need to install it from github.
It need at least python 3.6.

### For users

```
python3.6 -m pip install --user git+https://github.com/freeh4cker/emg_analyzer.git#egg=emg_analyzer
```

### For developers

It's recommended to install *emg_analyzer* in a virtualenv

```
python3.6 -m venv emg_env
source emg_env/bin/activate
```

Then install the project in editable mode

```
pip install -e git+https://github.com/freeh4cker/emg_analyzer.git#egg=emg_analyzer
``` 

## quick start

TODO

## Contributing 

We encourage contributions, bug report, enhancement ... 
But before to do that we encourage to read [the contributing guide](.github/CONTRIBUTING.md).
