# battery_soc_simulator
Hourly state of charge simulator for PV connected energy storage.

* Supports DC and AC coupled home solar/storage systems
* Setup for use with Apache Beam
* Allows parallel computation of multiple simulation scenarios

## Inputs

* Simulation parameters including PV system size, 
inverter and storage characteristics, and target hour of day
* Time series of PV power values

## Outputs

* Simulated state of charge at the specified time of day

## Example pipeline
A basic example pipeline is provided in 

`socsim.pipelines.simulate_hourly_state_of_charge.py`

This demonstrates how to pair time series data with 
simulation parameters for state of charge estimation. It
assumes that the power time series has already been grouped
into daily blocks of 24 hours.

