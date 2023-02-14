#!/usr/bin/env python

from nanoleafapi import Nanoleaf
from nanoleafapi import RED, ORANGE, YELLOW, GREEN, LIGHT_BLUE, BLUE, PINK, PURPLE, WHITE
import datetime
from time import sleep
from suntime import Sun, SunTimeException
from collections import namedtuple, defaultdict


NANOLEAF_IP = "192.168.0.198"
SUNRISE_OFFSET_M = 0  # offset from sunrise in minutes.
SUNRISE_FADE_DURATION_S = 60*10
# How long past the deadline before an unexecuted event expires in minutes.
LAG_M = 10
PLUGIN_UUIDS = {
    "wheel": 	"6970681a-20b5-4c5e-8813-bdaebc4ee4fa",
    "flow": 	"027842e4-e1d6-4a4c-a731-be74a1ebd4cf",
    "explode": 	"713518c1-d560-47db-8991-de780af71d1e",
    "fade": 	"b3fd723a-aae8-4c99-bf2b-087159e0ef53",
    "random": 	"ba632d3e-9c2b-4413-a965-510c839b3f71",
    "highlight": 	"70b7c636-6bf8-491f-89c1-f4103508d642",
}
nl = Nanoleaf(NANOLEAF_IP)
ran_log = defaultdict(lambda: False)  # Register of events already ran.
Event = namedtuple("Event", ['t', 'name', 'fn'])


def has_expired(t: datetime):
    return (t - datetime.datetime.now().astimezone()) < -datetime.timedelta(minutes=LAG_M)


def date_tomorrow():
    return datetime.date.today() + datetime.timedelta(days=1)


def plugin_lookup(name: str):
    return PLUGIN_UUIDS[name.lower()]


def get_sunrise_time(date: datetime.date):
    return Sun(42.317794, -72.631973).get_sunrise_time(date)


def display_sunrise_rising():
    nl.set_brightness(0, 0)
    nl.set_effect("Coral Sunrise")
    nl.set_brightness(0, 0)
    nl.set_brightness(100, duration=SUNRISE_FADE_DURATION_S)


def display_sunrise_risen():
    nl.set_effect("Wakeful Sunrise")
    nl.set_brightness(100, 30)


def mkev_sunrise_rising(day: datetime.date):
    """Before sunrise fade in Coral Sunrise"""
    return Event(get_sunrise_time(date=day)
                 + datetime.timedelta(minutes=SUNRISE_OFFSET_M)
                 + datetime.timedelta(seconds=-SUNRISE_FADE_DURATION_S),
                 "morning-sunrise", display_sunrise_rising)


def mkev_sunrise_risen(day: datetime.date):
    """At sunrise proper switch to Wakeful Sunrise"""
    return Event(get_sunrise_time(date=day)
                 + datetime.timedelta(minutes=SUNRISE_OFFSET_M),
                 "morning-sunrise", display_sunrise_risen)


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
    for mk_fn in [
        mkev_sunrise_rising,
        mkev_sunrise_risen,
        # At 10:15am turn off
        mkev_morning_off,
        # At 10pm turn on the nightlight
        mkev_nightlight,
    ]:
        schedule.append(mkev(mk_fn))

    schedule.append(mkev(lambda day: Event(
        datetime.datetime.combine(
            day,
            datetime.time(hour=9, minute=18)).astimezone(),
        "probe-1", display_sunrise_risen)))

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
    print("sleeping", sleep_for, flush=True)
    sleep(sleep_for.total_seconds())


if __name__ == "__main__":
    while True:
        loop_one()

# Panel info
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

# Coral sunrise effect
"""
{'version': '2.0',
 'animName': 'Coral Sunrise',
 'animType': 'plugin',
 'colorType': 'HSB',
 'palette': [
  {'hue': 5, 'saturation': 61, 'brightness': 100, 'probability': 0.0},
  {'hue': 340, 'saturation': 31, 'brightness': 87, 'probability': 0.0},
  {'hue': 38, 'saturation': 76, 'brightness': 100, 'probability': 0.0}],
 'pluginType': 'color',
 'pluginUuid': '6970681a-20b5-4c5e-8813-bdaebc4ee4fa',
 'pluginOptions': [{'name': 'linDirection', 'value': 'right'},
  {'name': 'loop', 'value': True},
  {'name': 'nColorsPerFrame', 'value': 2},
  {'name': 'transTime', 'value': 24}],
 'hasOverlay': False}
"""

# Wakeful sunrise
"""
nl.write_effect({
    "command": "add",
    'animName': 'Wakeful Sunrise',
    'animType': 'plugin',
    'colorType': 'HSB',
    'palette': [
        {'hue': 201, 'saturation': 61, 'brightness': 100, 'probability': 0.0},
        {'hue': 17, 'saturation': 8, 'brightness': 100, 'probability': 0.0},
    ],
    'pluginType': 'color',
    'pluginUuid': plugin_lookup('random'),
    'pluginOptions': [
        {'name': 'transTime', 'value': 30},
        {'name': 'delayTime', 'value': 10},
    ],
    'hasOverlay': False
})
"""
