"""
Classes defining types of residential installations and simulation configurations
"""


class ResidentialPVStorageSystem:
    """
    Class representing a residential solar/storage system.
    Currently assumes a single inverter, single battery system
    """

    def __init__(self,
                 storage_max_capacity: float,
                 storage_min_capacity: float,
                 storage_charging_efficiency: float,
                 inverter_max_power: float):
        # max capacity of the storage system
        self.storage_max_capacity = storage_max_capacity
        self.storage_min_capacity = storage_min_capacity
        self.storage_charging_efficiency = storage_charging_efficiency
        self.inverter_max_power = inverter_max_power


class DcCoupledSystem(ResidentialPVStorageSystem):
    """
    Class describing a DC coupled residential solar installation.
    In this type of system, a single inverter is connected to both the PV array and a battery.
    PV is metered on the AC side of the inverter, although the battery is connected to the DC side of the inverter
    Assumes a single inverter, single battery system
    """

    def __init__(self,
                 storage_max_capacity: float,
                 storage_min_capacity: float,
                 storage_charging_efficiency: float,
                 inverter_max_power: float,
                 inverter_dc_dc_efficiency: float,
                 inverter_dc_dc_max_power: float):
        super().__init__(storage_max_capacity, storage_min_capacity,
                         storage_charging_efficiency, inverter_max_power)
        # max power when PV power is used for battery charging
        self.inverter_dc_dc_max_power = inverter_dc_dc_max_power
        # inverter efficiency loss between PV and battery charging on the DC/DC side of the inverter
        self.inverter_dc_dc_efficiency = inverter_dc_dc_efficiency

    def get_charging_power(self, pv_power_kw: float) -> float:
        """
        Calculate the charging power to the battery based on the given PV output in one hour.
        Since

        :param pv_power_kw: Average PV power produced during an 1 hour time window
        :return: charging power to the battery
        """
        return (
                min(self.inverter_dc_dc_max_power, pv_power_kw)
                * self.inverter_dc_dc_efficiency
                * self.storage_charging_efficiency
        )


class AcCoupledSystem(ResidentialPVStorageSystem):
    """
    Class representing an AC coupled solar/storage system.
    In this installation, the inverter is connected to the PV array, and the battery is connected
    on the AC side of the inverter. The battery converts the AC power back to DC internally during charging.
    """

    def __init__(self, storage_max_capacity, storage_min_capacity,
                 storage_charging_efficiency, inverter_max_power):
        super().__init__(storage_max_capacity, storage_min_capacity,
                         storage_charging_efficiency, inverter_max_power)

    def get_charging_power(self, pv_power_kw: float) -> float:
        """
        Get the charging power to the battery given the specified battery power
        :param pv_power_kw: Average PV power produced during an 1 hour time window
        :return: charging power to the battery
        """
        return min(self.inverter_max_power, pv_power_kw) * self.storage_charging_efficiency
