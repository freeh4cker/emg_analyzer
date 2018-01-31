# EMG Analyzer
[![Build Status](https://travis-ci.org/freeh4cker/emg_analyzer.svg?branch=master)](https://travis-ci.org/freeh4cker/emg_analyzer)
[![Coverage Status](https://coveralls.io/repos/github/freeh4cker/emg_analyzer/badge.svg?branch=master)](https://coveralls.io/github/freeh4cker/emg_analyzer?branch=master)


Is a tool set to help to analyze ElectroMyoGraphy recorded via smart analyzer.
For now it is able to normalize The voltage from an Electromyography recorded file (.emt file)
and produce a new .emt file with the normalized voltage, this new file can be open in smart analyzer.
The second script allow to generate new emt grouped by tracks. 

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

:construction:

### emg_norm

To normalize tracks in emt file. There is to way to normalize tracks.

* all tracks are considered together to normalize (default)
* normalize tracks by tracks
   
```
emg_norm -v foo.emt

emg_norm -v --by-track foo.emt
```

### emg_group_tracks

emg_group_tracks take several emt files as input and groups tracks base on their names.
Creates one .emt file by tracks. for instance:

```
emg_group_tracks exp{1,2,3}.emt 
```

#### with inputs


    exp1.emt
      track_A track_B track_C track_D

    exp2.emt
      track_B track_A track_D track_D

    exp3.emt
      track_D track_C track_D track_C


#### create outputs


    track_A.emt
        exp1 exp2 exp3

    track_B.emt
        exp1 exp2 exp3

    track_C.emt
        exp1 exp2 exp3

    track_D.emt
        exp1 exp2 exp3



> **Note:**
> you can pipe the 2 methods
> ```
> emg_group_tracks exp{1,2,3}.emt | emg_norm -v
> ```
> create outputs:
>
> track_A.emt , track_B.emt, track_C.emt, track_D.emt, 
> track_A_norm.emt , track_B_norm.emt, track_C_norm.emt, track_D_norm.emt

## Contributing 

We encourage contributions, bug report, enhancement ... 

But before to do that we encourage to read [the contributing guide](CONTRIBUTING.md).
