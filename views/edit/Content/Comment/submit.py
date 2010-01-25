# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# SilvaForum
# Python

from Products.Silva import mangle
from Products.Formulator.Errors import FormValidationError
from Products.Silva.i18n import translate as _
from zope.i18n import translate

model = context.REQUEST.model
view = context

try:
    result = view.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error",
        message=context.render_form_errors(e))

changed = []
old_title = mangle.entities(model.get_title())
if old_title != result['object_title']:
    model.sec_update_last_author_info()
    model.set_title(result['object_title'])

    message = _('${old_title} to ${new_title}',
                mapping={
                    'old_title': old_title,
                    'new_title': mangle.entities(model.get_title())
                    })
    changed.append(('title', translate(message)))

newvalue = result['text']
if model.get_text() != newvalue:
    model.set_text(newvalue)
    model.sec_update_last_author_info()
    changed.append(translate(_('text updated')))

# FIXME: should put in message
# XXX: I don't understand the FIXME message.
message = _("Properties changed: ${changed}",
            mapping={'changed': context.quotify_list_ext(changed)})
return view.tab_edit(message_type="feedback", message=message)
