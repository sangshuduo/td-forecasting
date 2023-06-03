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
python mockdata.py
```

### Forecasting and show the result

```
python forecast.py
```

### Forecasting and dump to file

```
python forecast.py --dump forecast-result.png
```

## Commmand line argument list

usage: forecast.py [-h] [--dump DUMP]

Forecast power consumption program

options:
  -h, --help   show this help message and exit
  --dump DUMP  dump forecast picture to file
