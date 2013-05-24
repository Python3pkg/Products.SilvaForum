# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Products.Silva.testing import SilvaLayer
from Products.SilvaMetadata.interfaces import IMetadataService
from silva.app.subscriptions import interfaces as subscriptions
from silva.core.services.interfaces import IMemberService
from zope.component import getUtility, getMultiAdapter
from zope.publisher.browser import TestRequest
import Products.SilvaForum
import transaction

# A set of helpers for the tests

def get_captcha_word(browser):
    headers = browser.cookies.get_request_headers()
    request = TestRequest(HTTP_COOKIE=headers['Cookie'])
    captcha = getMultiAdapter((object(), request), name='captcha')
    return captcha._generate_words()[1]


def set_member_email(member_id, email):
    member = getUtility(IMemberService).get_member(member_id)
    assert member is not None
    member.set_email(email)


def enable_subscription(content):
    service = getUtility(subscriptions.ISubscriptionService)
    service.enable_subscriptions()
    service._from = 'notification@example.com' # A more human sized from
    manager = subscriptions.ISubscriptionManager(content)
    manager.subscribability = subscriptions.SUBSCRIBABLE


def enable_anonymous_posting(content):
    metadata = getUtility(IMetadataService).getMetadata(content)
    metadata.setValues('silvaforum-forum', {'anonymous_posting': 'yes'})


def enable_unauthenticated_posting(content):
    metadata = getUtility(IMetadataService).getMetadata(content)
    metadata.setValues(
        'silvaforum-forum',
        {'unauthenticated_posting': 'yes', 'anonymous_posting': 'yes'})



class ForumLayer(SilvaLayer):
    default_products = SilvaLayer.default_products + [
        'SilvaForum',
        ]

    def _install_application(self, app):
        super(ForumLayer, self)._install_application(app)
        app.root.service_extensions.install('SilvaForum')
        transaction.commit()


FunctionalLayer = ForumLayer(Products.SilvaForum)
