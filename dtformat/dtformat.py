# Copyright (c) 2007-2008 Infrae. All rights reserved.
# See also LICENSES.txt
# SilvaForum
# Python

from datetime import datetime, timedelta
from zope.i18n import translate

from Products.SilvaForum.i18n import translate as _

def format_dt(self, formatdate, currentdate=None):
    """
    Format a datetime return string 
    """
    dt = currentdate - formatdate
    if isinstance(dt, float):
        # XXX args are zope's DateTime instances rather than datetimes...
        dt = timedelta(dt)
    if dt.days > 28:
        return str(formatdate)

    ret = format_items(self, dt)
    
    if not ret:
        return _('Just added')
    if len(ret) > 2:
        str_format = ', '.join(ret[:-1])
        msg = _('Added ${time} ago', mapping={'time':str_format})
        #return 'Added ' + ', '.join(ret[:-1]) + ' ago'
        return msg
    else:
        str_format = ', '.join(ret)
        msg = _('Added ${time} ago', mapping={'time':str_format})
        #return 'Added ' + ', '.join(ret) + ' ago'
        return msg

def format_items(self, dt):

    # calculate time units
    weeks = int(dt.days / 7)
    days = dt.days % 7

    hours = int(dt.seconds / 3600)
    seconds = dt.seconds % 3600
    minutes = int(seconds / 60)

    # translation helper
    def _(str, **kwargs):
        kwargs['context'] = self.request
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
