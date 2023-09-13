# Battery Module User Guide

[[中文](./README-zh.md)]

## Introduction

> This module is used to query the battery level, voltage, and charging status of the current device.

## API Documentation

### Instantiate an Object

**Example:**

```python
from battery import Battery

adc_args = (adc_num, adc_period, factor)
chrg_gpion = 0
stdby_gpion = 1

battery = Battery(adc_args=adc_args, chrg_gpion=chrg_gpion, stdby_gpion=stdby_gpion)
```

**Parameters:**

|Parameter|Type|Description|
|:---|---|---|
|`adc_args`|tuple|Element 1: [ADC channel](https://python.quectel.com/doc/API_reference/en/peripherals/misc.ADC.html#Constants).<br>Element 2: Number of ADC readings in a loop.<br>Element 3: Calculation factor, optional.|
|`chrg_gpion`|int|CHRG (Pin 1): Charging status indication with open-drain output (Optional).|
|`stdby_gpion`|int|STDBY (Pin 5): Battery charging completion indication (Optional).|

### set_charge_callback

> Charging event callback function

**Example:**

```python
def charge_callback(charge_status):
    print(charge_status)

res = battery.set_charge_callback(charge_callback)
```

**Parameters:**

|Parameter|Type|Description|
|:---|---|---|
|charge_callback|function|Charging event callback function, callback function parameter is the device charging status:<br>0 - not charging.<br>1 - charging.<br>2 - charging completed.|

**Returns:**

|Data Type|Description|
|:---|---|
|bool|`True` for success, `False` for failure|

### set_temp

> Set the current working environment temperature of the device for calculating the device's battery level.

**Example:**

```python
res = battery.set_temp(20)
```

**Parameters:**

|Parameter|Type|Description|
|:---|---|---|
|temp|int/float|Temperature value, unit: Celsius|

**Returns:**

|Data Type|Description|
|:---|---|
|bool|`True` for success, `False` for failure|

### voltage

> Query the battery voltage

**Example:**

```python
battery.voltage
# 523
```

**Returns:**

|Data Type|Description|
|:---|---|
|int|Battery voltage, unit: mV|

### energy

> Query the battery level

**Example:**

```python
res = battery.energy
# 100
```

**Returns:**

|Data Type|Description|
|:---|---|
|int|Battery level in percentage, 0~100|

### charge_status

> Query the charging status

**Example:**

```python
battery.charge_status
```

**Returns:**

|Data Type|Description|
|:---|---|
|int|0 - Not charging<br>1 - Charging<br>2 - Charging completed|

## Usage Example

```python
from battery import Battery

# Instantiate the object
adc_args = (adc_num, adc_period, factor)
chrg_gpion = 0
stdby_gpion = 1
battery = Battery(adc_args=adc_args, chrg_gpion=chrg_gpion, stdby_gpion=stdby_gpion)

def charge_callback(charge_status):
    print(charge_status)

# Set the charging status callback function
battery.set_charge_callback(charge_callback)
# True

# Set the current device temperature
temp = 30
battery.set_temp(temp)
# True

# Get the current battery voltage
battery.voltage
# 3000

# Get the current battery level
battery.energy
# 100

# Get the current charging status
battery.charge_status
# 1

```