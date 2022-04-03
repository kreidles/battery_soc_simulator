import apache_beam as beam
from socsim.models.simulation_config import StateOfChargeSimulationConfig
from typing import Tuple, Dict, Iterable


class SimulateStateOfCharge(beam.DoFn):
    """
    Apache Beam PTransform that takes a simulation config with a PV power time series
    and yields a PCollection of simulated state of charge values
    """
    def process(self, element: Tuple[Iterable[Dict], StateOfChargeSimulationConfig]):
        """
        Beam processing function. Simulates state of charge for a 24 hour PV power time series and
        a simulation configuration describing the type of system, PV size, and target hour of day
        :param element: PCollection of tuples pairing a simulation config with a 24 hour PV power time series
        :return:
        """
        (power_ts, sim_config) = element
        charging_energy = 0.0
        for pv_power_interval in power_ts:
            if pv_power_interval["hour_of_day"] < sim_config.target_hour_of_day:
                charging_energy += sim_config.system_spec.get_charging_power(
                    pv_power_interval["power"] * sim_config.pv_system_size)

        state_of_charge = (
                100
                * min(sim_config.system_spec.storage_max_capacity,
                      sim_config.system_spec.storage_min_capacity + charging_energy)
                / sim_config.system_spec.storage_max_capacity
        )

        yield {"config": sim_config, "state_of_charge": state_of_charge}

