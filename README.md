# td-forecasting
Forecasting with TDengine

## Prerequisite

### Install TDengine

Please download TDengine official installation package from the official website or build it from [the source code](https://github.com/taosdata/TDengine) then install TDengine to your system.

### Install Python3 pip to install required packages

```
python -m pip install -r requirements.txt
```

## Usage

### Mock data

```
python mockdata.py [--devices NUM_OF_DEVICES]
```

### Forecasting and show the result

```
python forecast.py
```

### [WIP] Forecasting and show the result on console

```
python forecast.py --plotext
```

### Forecasting and dump to file

```
python forecast.py --dump forecast-result.png
```

## Command line argument list

usage: forecast.py [-h] [--dump DUMP] [--plotext]

Forecast power consumption program

options:
  -h, --help   show this help message and exit
  --dump DUMP  dump forecast picture to file
  --plotext    plot forecast picture in console mode
