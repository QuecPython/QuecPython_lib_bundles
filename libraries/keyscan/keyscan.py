# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#     http://www.apache.org/licenses/LICENSE-2.0
#  
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from machine import ExtInt
from machine import Pin
from utime import sleep_ms
from queue import Queue
import _thread
import osTimer

key_evt_queue = Queue(8)

def key_evt_thread_entry():
    while True:
        self, event = key_evt_queue.get()
        self.event_cb(self, event)

_thread.start_new_thread(key_evt_thread_entry, ())

class Key():

    class Event():
        PRESSED = 0x01
        RELEASED = 0x02
        LONG_PRESSED = 0x04

    class Error(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    def __init__(self, pin, level_on_pressed, cared_event, event_cb, long_press_event = []):
        self.pin = pin
        if level_on_pressed == 0:
            self.exti_pull = ExtInt.PULL_PU
            if cared_event == self.Event.PRESSED:
                self.exti_trigger_mode = ExtInt.IRQ_FALLING
            elif cared_event == self.Event.RELEASED:
                self.exti_trigger_mode = ExtInt.IRQ_RISING
            elif cared_event == self.Event.PRESSED | self.Event.RELEASED:
                self.exti_trigger_mode = ExtInt.IRQ_RISING_FALLING
            else:
                raise self.Error("Value error of <cared_event>!")
        elif level_on_pressed == 1:
            self.exti_pull = ExtInt.PULL_PD
            if cared_event == self.Event.PRESSED:
                self.exti_trigger_mode = ExtInt.IRQ_RISING
            elif cared_event == self.Event.RELEASED:
                self.exti_trigger_mode = ExtInt.IRQ_FALLING
            elif cared_event == self.Event.PRESSED | self.Event.RELEASED:
                self.exti_trigger_mode = ExtInt.IRQ_RISING_FALLING
            else:
                raise self.Error("Value error of <cared_event>!")
        else:
            raise self.Error("Value error of <level_on_pressed>!")

        self.level_on_pressed = level_on_pressed
        self.cared_event = cared_event
        self.event_cb = event_cb
        self.long_press_event = long_press_event
        self.exti = ExtInt(self.pin, self.exti_trigger_mode, self.exti_pull, self.exit_cb)
        self.exti.enable()
        self.timer = osTimer()
        self.sec = 0

    def timer_cb(self, args):
        self.sec += 1
        for n in self.long_press_event:
            if self.sec == n:
                key_evt_queue.put((self, self.Event.LONG_PRESSED))
                break

    def exit_cb(self, args):
        self.exti.disable()
        sleep_ms(20)
        gpio = Pin(args[0], Pin.IN, Pin.PULL_PU, 1)
        level = gpio.read()
        event = None

        if self.level_on_pressed == 0:
            if level == 0:
                event = self.Event.PRESSED
            else:
                event = self.Event.RELEASED
        else:
            if level == 1:
                event = self.Event.PRESSED
            else:
                event = self.Event.RELEASED

        if event & self.cared_event:
            key_evt_queue.put((self, event))

        if event == self.Event.PRESSED:
            self.sec = 0
            self.timer.start(1000, 1, self.timer_cb)
        else:
            self.timer.stop()

        self.exti = ExtInt(self.pin, self.exti_trigger_mode, self.exti_pull, self.exit_cb)
        self.exti.enable()

if __name__ == '__main__':
    k1 = Pin.GPIO4
    k2 = Pin.GPIO30

    def event_cb(k, event):
        if event != Key.Event.LONG_PRESSED:
            print("%s is %s" % ("k1" if k.pin == k1 else "k2", "pressed" if event == Key.Event.PRESSED else "released"))
            if event == Key.Event.RELEASED:
                print("do something when key is released after %d seconds" % k.sec)
        else:
            print("%s is pressed for %d seconds" % ("k1" if k.pin == k1 else "k2", k.sec))

    Key(k1, 0, Key.Event.PRESSED | Key.Event.RELEASED, event_cb)
    Key(k2, 0, Key.Event.PRESSED | Key.Event.RELEASED, event_cb, [2, 4, 6])