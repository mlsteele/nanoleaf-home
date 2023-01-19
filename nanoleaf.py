#!/usr/bin/env python

from nanoleafapi import Nanoleaf
from nanoleafapi import RED, ORANGE, YELLOW, GREEN, LIGHT_BLUE, BLUE, PINK, PURPLE, WHITE
import datetime
from dateutil.tz import tzutc
from time import sleep
from suntime import Sun, SunTimeException
from collections import namedtuple, defaultdict

NANOLEAF_IP = "192.168.0.198"
SUNRISE_OFFSET_M = 0  # offset from sunrise in minutes.
# How long past the deadline before an unexecuted event expires in minutes.
LAG_M = 10

nl = Nanoleaf(NANOLEAF_IP)
ran_log = defaultdict(lambda: False)  # Register of events already ran.


def display_sunrise():
    nl.set_effect("Coral Sunrise")
    nl.set_brightness(100)  # 0 - 100


Event = namedtuple("Event", ['t', 'name', 'fn'])


def has_expired(t: datetime):
    return (t - datetime.datetime.now().astimezone()) < -datetime.timedelta(minutes=LAG_M)


def date_tomorrow():
    return datetime.date.today() + datetime.timedelta(days=1)


def mkev_sunrise(day: datetime.date):
    """At sunrise turn on coral sunrise"""
    sun = Sun(42.317794, -72.631973)
    return Event(sun.get_sunrise_time(date=day)
                 + datetime.timedelta(minutes=SUNRISE_OFFSET_M),
                 "morning-sunrise", display_sunrise)


def mkev_morning_off(day: datetime.date):
    return Event(datetime.datetime.combine(
        day,
        datetime.time(hour=10, minute=15)).astimezone(),
        "morning-off", lambda: nl.power_off())


def mkev_nightlight(day: datetime.date):
    return Event(datetime.datetime.combine(
        day, datetime.time(hour=20)).astimezone(),
        "nightlight-on", lambda: nl.set_color((0.13 * 255, 0, 0)))


def mkev(mk_fn):
    ev = mk_fn(datetime.date.today())
    if has_expired(ev.t):
        ev = mk_fn(date_tomorrow())
    return ev


def already_ran(ev, insert=False):
    res = ran_log[(ev.t, ev.name)]
    if insert:
        ran_log[(ev.t, ev.name)] = True

    # cleanup
    for x in ran_log:
        if x[0] - datetime.datetime.now().astimezone() < -datetime.timedelta(days=2):
            del ran_log[x]
    return res


def get_schedule():
    """Get a list of upcoming Events."""
    schedule = []
    sun = Sun(42.317794, -72.631973)
    # At sunrise turn on coral sunrise
    schedule.append(mkev(mkev_sunrise))

    # At 10:15am turn off
    schedule.append(mkev(mkev_morning_off))

    # At 10pm turn on the nightlight
    schedule.append(mkev(mkev_nightlight))

    # schedule.append(mkev(lambda day: Event(
    #     datetime.datetime.combine(
    #         day,
    #         datetime.time(hour=8, minute=56)).astimezone(),
    #     "probe-1", lambda: nl.set_color((0, 0, 100)))))

    # schedule.append(mkev(lambda day: Event(
    #     datetime.datetime.combine(
    #         day,
    #         datetime.time(hour=8, minute=57)).astimezone(),
    #     "probe-2", lambda: nl.set_color((0, 100, 0)))))

    schedule = filter(lambda ev: not already_ran(ev), schedule)
    return sorted(schedule, key=lambda x: x[0])


has_expired(datetime.datetime.combine(datetime.date.today(),
            datetime.time(hour=8, minute=39)).astimezone())


def loop_one():
    print("---")
    schedule = get_schedule()
    SLEEP_MIN = datetime.timedelta(seconds=1)
    SLEEP_MAX = datetime.timedelta(minutes=20)
    sleep_for = SLEEP_MAX
    if len(schedule) > 0:
        print("schedule")
        for t, name, _ in schedule:
            print(t, name)
        ev = schedule[0]
        until = ev.t - datetime.datetime.now().astimezone()
        print(until, "until", ev.name)
        if until <= datetime.timedelta(minutes=0):
            print("running", ev.name)
            ev.fn()
            already_ran(ev, insert=True)
            return
        else:
            sleep_for = until
    sleep_for = max(min(sleep_for, SLEEP_MAX), SLEEP_MIN)
    print("sleeping", sleep_for)
    sleep(sleep_for.total_seconds())


if __name__ == "__main__":
    while True:
        loop_one()

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
