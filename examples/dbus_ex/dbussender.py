import threading
import sys
import time
import signal as sig
from pydbus import SessionBus
from pydbus.generic import signal
from gi.repository import GLib
from piracer.vehicles import PiRacerStandard
from piracer.gamepads import ShanWanGamepad  # 네가 가진 gamepad.py import

class GamepadService(object):
    """
    <node>
      <interface name='org.team9.IC'>
        <property name='Throttle' type='s' access='read'/>
        <property name='Steering' type='s' access='read'/>
        <signal name='ValueChanged'>
          <arg type='s' name='key'/>
          <arg type='s' name='value'/>
        </signal>
      </interface>
    </node>
    """

    ValueChanged = signal()
    def __init__(self):
        self.Throttle = "none"
        self.Steering = "none"
        self.Voltage = "none"
        self.Current = "none"
        self.Power_Consumtion = "none"

    def emit_value_changed(self, key, value):
        print(f"[Signal] {key} -> {value}")
        self.ValueChanged(key, value)

def gamepad_loop(pad, service):
    MIN_TH = 0.125
    while True:
        data = pad.read_data()  # blocking

        # steering: L.x (left <-> right)
        steering = "none"
        if data.analog_stick_left.x > MIN_TH:
            steering = "right"
        elif data.analog_stick_left.x < -MIN_TH:
            steering = "left"

        if steering != service.Steering:
            service.Steering = steering
            service.emit_value_changed("Steering", steering)

        # throttle: R.y (forward <-> backward)
        throttle = "none"
        if data.analog_stick_right.y > MIN_TH:
            throttle = "forward"
        elif data.analog_stick_right.y < -MIN_TH:
            throttle = "backward"

        if throttle != service.Throttle:
            service.Throttle = throttle
            service.emit_value_changed("Throttle", throttle)

def main():
    piracer = PiRacerStandard()
    bus = SessionBus()
    service = GamepadService()
    bus.publish("org.team9.IC", service)
    print("🚀 GamepadService published on DBus: org.team9.IC")

    # 조이스틱 초기화
    pad = ShanWanGamepad()
    MIN_TH = 0.125
    def update_battery_info():
        service.Voltage = str(piracer.get_battery_voltage())
        service.emit_value_changed("Voltage", service.Voltage)
        service.Current = str(piracer.get_battery_current())
        service.emit_value_changed("Current", service.Current)
        service.Power_Consumtion = str(piracer.get_power_consumption())
        service.emit_value_changed("Power_Consumtion", service.Power_Consumtion)
        return True

    # a thread for blocking task (read_data() from gamepad)
    threading.Thread(target=gamepad_loop, args=(pad, service), daemon=True).start()
    #GLib.timeout_add(100, poll_gamepad)
    GLib.timeout_add(2000, update_battery_info)
    loop = GLib.MainLoop()

    # to make process can read SIGINT (Ctrl+C)
    def handle_sigint(signum, frame):
        print("\nReceived SIGINT, exiting...")
        loop.quit()  # GLib 이벤트 루프 종료
        sys.exit(0)  # 프로그램 종료

    sig.signal(sig.SIGINT, handle_sigint)

    loop.run()


if __name__ == "__main__":
    main()

