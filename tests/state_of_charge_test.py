import json
import unittest
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that
from apache_beam.testing.util import equal_to

from socsim.models.residential import DcCoupledSystem, AcCoupledSystem
from socsim.models.simulation_config import StateOfChargeSimulationConfig
from socsim.transformers.state_of_charge import SimulateStateOfCharge


def get_rounded_soc(soc: float):
    yield round(soc, 2)


class TestStateOfChargeSimulation(unittest.TestCase):
    """
    Tests for individual transformers in the solar data tool pipeline
    """
    dc_spec = DcCoupledSystem(
        storage_max_capacity=10.0,
        storage_min_capacity=2.0,
        storage_charging_efficiency=0.98,
        inverter_max_power=7.0,
        inverter_dc_dc_efficiency=0.95,
        storage_max_charging_power=5.0
    )
    ac_spec = AcCoupledSystem(
        storage_max_capacity=13.5,
        storage_min_capacity=1.0,
        storage_charging_efficiency=0.91,
        inverter_max_power=7.0,
    )
    power_ts = list(map(json.loads, open('data/power_ts.ndjson')))[0]
    x = 1

    def test_state_of_charge_dc(self):
        """
        Test calculation of state of charge for a DC Coupled system
        """
        dc_sim_inputs = [
            (self.power_ts, StateOfChargeSimulationConfig(self.dc_spec, 2.0, 12)),
            (self.power_ts, StateOfChargeSimulationConfig(self.dc_spec, 2.0, 15)),
            (self.power_ts, StateOfChargeSimulationConfig(self.dc_spec, 2.0, 17)),
        ]

        expected_output = [52.59, 84.43, 99.69]
        # Create a test pipeline.
        with TestPipeline() as p:
            output = (
                    p
                    | "Make a test Pcollection" >> beam.Create(dc_sim_inputs)
                    | "Check the value" >> beam.ParDo(SimulateStateOfCharge())
                    | "Round SOC value" >> beam.FlatMap(lambda x: get_rounded_soc(x['state_of_charge']))
            )

            # Assert on the results.
            assert_that(
                output,
                equal_to(expected_output)
            )

    def test_state_of_charge_ac(self):
        """
        Test calculation of state of charge for a DC Coupled system
        """
        ac_sim_inputs = [
            (self.power_ts, StateOfChargeSimulationConfig(self.ac_spec, 2.0, 12)),
            (self.power_ts, StateOfChargeSimulationConfig(self.ac_spec, 2.0, 15)),
            (self.power_ts, StateOfChargeSimulationConfig(self.ac_spec, 2.0, 17)),
        ]

        expected_output = [31.0, 54.05, 65.11]
        # Create a test pipeline.
        with TestPipeline() as p:
            output = (
                    p
                    | "Make a test Pcollection" >> beam.Create(ac_sim_inputs)
                    | "Check the value" >> beam.ParDo(SimulateStateOfCharge())
                    | "Round SOC value" >> beam.FlatMap(lambda x: get_rounded_soc(x['state_of_charge']))
            )

            # Assert on the results.
            assert_that(
                output,
                equal_to(expected_output)
            )


if __name__ == '__main__':
    unittest.main()
