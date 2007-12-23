# Copyright (c) 2007 Infrae. All rights reserved.
# See also LICENSES.txt
# SilvaForum
# Python

from datetime import datetime, timedelta

def format_dt(formatdate, currentdate=None):
    """
    Format a datetime return string 
    """
    dt = currentdate - formatdate
    if isinstance(dt, float):
        # XXX args are zope's DateTime instances rather than datetimes...
        dt = timedelta(dt)
    if dt.days > 28:
        return str(formatdate)

    # calculate time units
    weeks = int(dt.days / 7)
    days = dt.days % 7

    hours = int(dt.seconds / 3600)
    seconds = dt.seconds % 3600
    minutes = int(seconds / 60)

    # format a time unit to singular or plural
    weekstring = empty_singular_plural(weeks, 'week')
    daystring = empty_singular_plural(days, 'day')
    hourstring = empty_singular_plural(hours, 'hour')
    minutestring = empty_singular_plural(minutes, 'minute')

    # check if timer unit has value then append to list
    ret = []
    if weekstring:
        ret.append(weekstring)
    if daystring:
        ret.append(daystring)
    if hourstring:
        ret.append(hourstring)
    if minutestring:
        ret.append(minutestring)
    if not ret:
        return 'Just added'
    if len(ret) > 2:
        return 'Added ' + ', '.join(ret[:-1]) + ' ago'
    else:
        return 'Added ' + ', '.join(ret) + ' ago'

# XXX oomph, bad name...
def empty_singular_plural(num, unitname):
    ret = ''
    if num:
        ret = '%s %s' % (num, unitname)
        if num > 1:
            ret += 's'
    return ret

