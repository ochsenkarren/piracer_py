#!/usr/bin/env python3
import sys
import time
import signal as sig
from pydbus import SessionBus
from pydbus.generic import signal
from gi.repository import GLib

from piracer.gamepads import ShanWanGamepad  # 네가 가진 gamepad.py import

class GamepadService(object):
    """
    <node>
      <interface name='org.example.Gamepad'>
        <property name='Throttle' type='s' access='read'/>
        <property name='Steering' type='s' access='read'/>
        <property name='Speed' type='i' access='read'/>
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
        self.Speed = 0

    def emit_value_changed(self, key, value):
        print(f"[Signal] {key} -> {value}")
        self.ValueChanged(key, value)


def main():
    bus = SessionBus()
    service = GamepadService()
    bus.publish("org.example.Gamepad", service)
    print("🚀 GamepadService published on DBus: org.example.Gamepad")

    # 조이스틱 초기화
    pad = ShanWanGamepad()
    MIN_TH = 0.125

    # GLib 타이머 루프에 등록 (100ms 간격)
    def poll_gamepad():
        data = pad.read_data()

        # throttle: L.y (앞뒤)
        if data.analog_stick_left.y > MIN_TH:
            throttle = "forward"
        elif data.analog_stick_left.y < -MIN_TH:
            throttle = "backward"
        else:
            throttle = "none"

        if throttle != service.Throttle:
            service.Throttle = throttle
            service.emit_value_changed("Throttle", throttle)

        # steering: R.x (좌우)
        if data.analog_stick_right.x > MIN_TH:
            steering = "right"
        elif data.analog_stick_right.x < -MIN_TH:
            steering = "left"
        else:
            steering = "none"

        if steering != service.Steering:
            service.Steering = steering
            service.emit_value_changed("Steering", steering)

        return True  # GLib 타이머 계속 실행

    GLib.timeout_add(100, poll_gamepad)
    loop = GLib.MainLoop()
    # SIGINT (Ctrl+C) 신호 처리
    def handle_sigint(signum, frame):
        print("\nReceived SIGINT, exiting...")
        loop.quit()  # GLib 이벤트 루프 종료
        sys.exit(0)  # 프로그램 종료

    sig.signal(sig.SIGINT, handle_sigint)

    loop.run()


if __name__ == "__main__":
    main()

