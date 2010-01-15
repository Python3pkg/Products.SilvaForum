# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

from datetime import datetime, timedelta
from zope.i18n import translate

from silva.translations import translate as _


def dtformat(request, formatdate, currentdate=None):
    """Format a datetime object into a nice human like string.
    """
    if currentdate is None:
        currentdata = datetime.now()
    dt = currentdate - formatdate
    if isinstance(dt, float):
        # XXX args are zope's DateTime instances rather than datetimes...
        dt = timedelta(dt)
    if dt.days > 28:
        return str(formatdate)

    parts = dtformat_timedelta(request, dt)
    # translation helper
    def _(str, **kwargs):
        kwargs['context'] = request
        kwargs['domain'] = 'silvaforum'
        return translate(str, **kwargs)

    if not parts:
        return _('Just added')
    if len(parts) > 2:
        str_format = ', '.join(parts[:-1])
        return _('Added ${time} ago', mapping={'time': str_format})
    else:
        str_format = ', '.join(parts)
        return _('Added ${time} ago', mapping={'time': str_format})


def dtformat_timedelta(request, dt):
    """Format a timedelta object in a nice human like string.
    """

    # calculate time units
    weeks = int(dt.days / 7)
    days = dt.days % 7

    hours = int(dt.seconds / 3600)
    seconds = dt.seconds % 3600
    minutes = int(seconds / 60)

    # translation helper
    def _(str, **kwargs):
        kwargs['context'] = request
        kwargs['domain'] = 'silvaforum'
        return translate(str, **kwargs)

    ret = []
    if weeks:
        if weeks == 1:
            ret.append(_('one week'))
        else:
            ret.append(_('${number} weeks', mapping={'number': weeks}))

    if days:
        if days == 1:
            ret.append(_('one day'))
        else:
            ret.append(_('${number} days', mapping={'number': days}))

    if hours:
        if hours == 1:
            ret.append(_('one hour'))
        else:
            ret.append(_('${number} hours', mapping={'number': hours}))

    if minutes:
        if minutes == 1:
            ret.append(_('one minute'))
        else:
            ret.append(_('${number} minutes', mapping={'number': minutes}))

    return ret
