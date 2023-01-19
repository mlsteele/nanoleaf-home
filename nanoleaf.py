#!/usr/bin/env python

from nanoleafapi import Nanoleaf
from nanoleafapi import RED, ORANGE, YELLOW, GREEN, LIGHT_BLUE, BLUE, PINK, PURPLE, WHITE
import datetime
from dateutil.tz import tzutc
from time import sleep
from suntime import Sun, SunTimeException
NANOLEAF_IP = "192.168.0.198"
nl = Nanoleaf(NANOLEAF_IP)

SUNRISE_OFFSET_M = 0  # offset from sunrise in minutes


def sunrise():
    nl.set_effect("Coral Sunrise")
    nl.set_brightness(100)  # 0 - 100


def get_schedule():
    """Return a list of events for today.
    [(datetime, name, fn), ...]
    """
    schedule = []
    sun = Sun(42.317794, -72.631973)
    # At sunrise turn on coral sunrise
    schedule.append((sun.get_sunrise_time()
                     + datetime.timedelta(minutes=SUNRISE_OFFSET_M),
                     "morning-sunrise", sunrise))

    # At 10:15am turn off
    # schedule.append((datetime.datetime.combine(datetime.date.today(), datetime.time(hour=10, minute=15, tzinfo=tzutc())),
    schedule.append((datetime.datetime.combine(
        datetime.date.today(), datetime.time(hour=10, minute=15)).astimezone(),
        "morning-off", lambda: nl.power_off()))

    # At 10pm turn on the nightlight
    schedule.append((datetime.datetime.combine(
        datetime.date.today(), datetime.time(hour=20)).astimezone(),
        "nightlight-on", lambda: nl.set_color((0.13 * 255, 0, 0))))

    # Fake testing thing
    schedule.append((datetime.datetime.combine(
        datetime.date.today(), datetime.time(hour=21, minute=14)).astimezone(),
        "nightlight-on", lambda: nl.set_color((0.13 * 255, 0, 0))))

    return sorted(schedule, key=lambda x: x[0])


if __name__ == "__main__":
    # Warning: This crappy scheduler may miss events scheduled within 20 minutes past midnight.
    while True:
        print("---")
        schedule = get_schedule()
        SLEEP_MIN = datetime.timedelta(seconds=1)
        SLEEP_MAX = datetime.timedelta(minutes=20)
        sleep_for = SLEEP_MAX
        if len(schedule) > 0:
            print("schedule")
            for t, name, _ in schedule:
                print(t, name)
            t, name, fn = schedule[0]
            until = t - datetime.datetime.now().astimezone()
            print(until, "until", name)
            if until < datetime.timedelta(minutes=10):
                pass
            elif until <= datetime.timedelta(minutes=0):
                print("running", name)
                fn()
            else:
                sleep_for = until
        sleep_for = max(min(sleep_for, SLEEP_MAX), SLEEP_MIN)
        print("sleeping", sleep_for)
        sleep(sleep_for.total_seconds())


"""
{'name': 'Light Panels 50:A2:58',
 'serialNo': 'S17072A2725',
 'manufacturer': 'Nanoleaf',
 'firmwareVersion': '5.1.0',
 'hardwareVersion': '1.6-2',
 'model': 'NL22',
 'cloudHash': {},
 'discovery': {},
 'effects': {'effectsList': ['Astroneer',
   'Color Burst',
   'Fireplace',
   'Forest',
   'Inner Peace',
   'Nemo',
   'Northern Lights',
   'Romantic',
   'Snake',
   'Snowfall',
   'Vibrant Sunrise',
   'Natural Light',
   'Coral Sunrise',
   'Slow Bright Sunrise',
   'Red'],
  'select': '*Dynamic*'},
 'firmwareUpgrade': {},
 'panelLayout': {'globalOrientation': {'value': 31, 'max': 360, 'min': 0},
  'layout': {'numPanels': 10,
   'sideLength': 150,
   'positionData': [{'panelId': 162,
     'x': 299,
     'y': 43,
     'o': 60,
     'shapeType': 0},
    {'panelId': 122, 'x': 299, 'y': 129, 'o': 240, 'shapeType': 0},
    {'panelId': 251, 'x': 374, 'y': 173, 'o': 180, 'shapeType': 0},
    {'panelId': 8, 'x': 224, 'y': 173, 'o': 300, 'shapeType': 0},
    {'panelId': 209, 'x': 224, 'y': 259, 'o': 240, 'shapeType': 0},
    {'panelId': 87, 'x': 299, 'y': 303, 'o': 300, 'shapeType': 0},
    {'panelId': 48, 'x': 149, 'y': 129, 'o': 0, 'shapeType': 0},
    {'panelId': 191, 'x': 75, 'y': 173, 'o': 300, 'shapeType': 0},
    {'panelId': 126, 'x': 0, 'y': 129, 'o': 0, 'shapeType': 0},
    {'panelId': 203, 'x': 149, 'y': 43, 'o': 180, 'shapeType': 0}]}},
 'rhythm': {'auxAvailable': None,
  'firmwareVersion': None,
  'hardwareVersion': None,
  'rhythmActive': None,
  'rhythmConnected': False,
  'rhythmId': None,
  'rhythmMode': None,
  'rhythmPos': None},
 'schedules': {},
 'state': {'brightness': {'value': 100, 'max': 100, 'min': 0},
  'colorMode': 'effect',
  'ct': {'value': 1200, 'max': 6500, 'min': 1200},
  'hue': {'value': 0, 'max': 360, 'min': 0},
  'on': {'value': True},
  'sat': {'value': 0, 'max': 100, 'min': 0}}}
"""
