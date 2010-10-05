# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import getSecurityManager
from Products.SilvaForum.interfaces import IPostable
from five import grok
from silva.core.interfaces import ISubscribable
from silva.core.views import views as silvaviews
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface

_ = MessageFactory('silvaforum')


class Subscriptions(silvaviews.ContentProvider):
    grok.context(IPostable)
    grok.view(Interface)

    email = ''
    email_missing = False
    invalid_captcha = False
    can_subscribe = True
    can_unsubscribe = True
    message = ''

    def extract_email(self, required=False):
        self.email = self.request.form.get('form.field.email', None)
        if self.email:
            if not isinstance(self.email, unicode):
                self.email = self.email.decode('utf-8')
        if required:
            if not self.email:
                self.message = _(u"There were errors.")
                self.email_missing = True
                return False
        return True

    def validate_captcha(self):
        if self.need_captcha:
            value = self.request.form.get('form.field.captcha', '')
            if not value:
                self.invalid_captcha = True
                self.message = _(u"Captcha value is missing.")
                return False
            captcha = getMultiAdapter(
                (self.context.aq_inner, self.request), name='captcha')
            if not captcha.verify(value):
                self.invalid_captcha = True
                self.message = _(u'Invalid captcha value.')
                return False
        return True


    def action_subscribe(self):
        if self.extract_email(True) and self.validate_captcha():
            service = self.context.aq_inner.service_subscriptions
            try:
                service.requestSubscription(self.context.aq_inner, self.email)
            except:
                self.message = _(
                    u"An error happened while subscribing you to the post.")
            else:
                self.message = _(
                    u"A confirmation mail have been sent for your subscription.")

    def action_unsubscribe(self):
        if self.extract_email(True) and self.validate_captcha():
            service = self.context.aq_inner.service_subscriptions
            try:
                service.requestCancellation(self.context.aq_inner, self.email)
            except:
                self.message = _(
                    u"An error happened while unsubscribing you to the post.")
            else:
                self.message = _(
                    u"A confirmation mail have been sent to unsubscribe you.")

    ACTIONS = {
        'form.action.subscribe': action_subscribe,
        'form.action.unsubscribe': action_unsubscribe}

    def update(self):
        user_id = getSecurityManager().getUser().getId()
        member = self.context.aq_inner.service_members.get_member(user_id)
        self.need_captcha =  member is None

        for key, action in self.ACTIONS.items():
            if key in self.request.form:
                action(self)
                break
        else:
            self.extract_email()
            if not self.email:
                if member is not None:
                    self.email = member.email()
        if member is not None and self.email:
            subscribable = ISubscribable(self.context.aq_inner)
            if subscribable.isSubscribed(self.email):
                self.can_subscribe = False
            else:
                self.can_unsubscribe = False
