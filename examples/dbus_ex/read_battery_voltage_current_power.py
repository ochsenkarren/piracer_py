# Copyright (C) 2022 twyleg
import time
from piracer.vehicles import PiRacerStandard, PiRacerPro


def print_energy_report():
    battery_bus_voltage = piracer.get_battery_bus_voltage()
    battery_shunt_voltage = piracer.get_battery_shunt_voltage()
    battery_voltage = piracer.get_battery_voltage()
    battery_current = piracer.get_battery_current()
    power_consumption = piracer.get_power_consumption()

    print('Bus voltage={0:0>6.3f}V, Shunt voltage={1:0>6.3f}V, Battery voltage={2:0>6.3f}V, \
\ncurrent={3:0>8.3f}mA, power={4:0>6.3f}W\n'.format(battery_bus_voltage, battery_shunt_voltage,\
 battery_voltage, battery_current, power_consumption))


if __name__ == '__main__':
    piracer = PiRacerStandard()

    while True :
        print_energy_report()
        time.sleep(2)
