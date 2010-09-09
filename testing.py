# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.testing import SilvaLayer
import Products.SilvaForum
import transaction


class SilvaForumLayer(SilvaLayer):
    default_products = SilvaLayer.default_products + [
        'SilvaForum',
        ]

    def _install_application(self, app):
        super(SilvaForumLayer, self)._install_application(app)
        app.root.service_extensions.install('SilvaForum')
        transaction.commit()


FunctionalLayer = SilvaForumLayer(
    Products.SilvaForum, zcml_file='configure.zcml')
