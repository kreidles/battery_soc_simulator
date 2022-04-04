import json

from socsim.models.residential import ResidentialPVStorageSystem, DcCoupledSystem, AcCoupledSystem


def simulation_config_from_text_line(line: str):
    """
    Helper to create a StateOfChargeSimulationConfig from an ndJSON file. JSON
    should have the following form
    {"pv_system_size": 3.4, "target_hour_of_day": 15, "type": "DC Coupled", ""
    :return:
    """
    config = json.loads(line)
    system_spec = None
    # ideally more validation of input fields here
    if config['type'] == 'DC Coupled':
        system_spec = DcCoupledSystem(
            storage_max_capacity=config['storage_max_capacity'],
            storage_min_capacity=config['storage_min_capacity'],
            storage_charging_efficiency=config['storage_charging_efficiency'],
            inverter_max_power=config['inverter_max_power'],
            inverter_dc_dc_efficiency=config['inverter_dc_dc_efficiency'],
            storage_max_charging_power=config['storage_max_charging_power']
        )
    else:
        # assume AC otherwise
        system_spec = AcCoupledSystem(
            storage_max_capacity=config['storage_max_capacity'],
            storage_min_capacity=config['storage_min_capacity'],
            storage_charging_efficiency=config['storage_charging_efficiency'],
            inverter_max_power=config['inverter_max_power']
        )

    yield StateOfChargeSimulationConfig(system_spec, config["pv_system_size"], config["target_hour_of_day"])


class StateOfChargeSimulationConfig:
    """
    Class containing options for hourly state of charge simulation
    """
    def __init__(self,
                 system_spec: ResidentialPVStorageSystem,
                 pv_system_size: float,
                 target_hour_of_day: int):
        self.system_spec = system_spec
        # set the PV system size to simulate
        if pv_system_size <= 0:
            raise Exception("PV system size must be greater than 0 kW")
        self.pv_system_size = pv_system_size
        # set the target hour of the day at which state of charge will be simulated
        if target_hour_of_day < 0 or target_hour_of_day > 23:
            raise Exception("PV system size must be greater than 0 kW")
        self.target_hour_of_day = target_hour_of_day

