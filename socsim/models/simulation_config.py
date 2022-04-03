from socsim.models.residential import ResidentialPVStorageSystem


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
