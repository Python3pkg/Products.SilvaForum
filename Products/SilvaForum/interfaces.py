# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 Infrae. All rights reserved.
# See also LICENSE.txt
# See also LICENSES.txt

from js.jquery import jquery
from silva.core import conf as silvaconf
from silva.core.interfaces import IContent, ISilvaObject, IContainer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IForumResources(IDefaultBrowserLayer):
    silvaconf.resource(jquery)
    silvaconf.resource('forum.js')
    silvaconf.resource('forum.css')


class IPostContent(Interface):
    """Identify all postable/post content.
    """

class IPostable(IPostContent, IContainer):
    """Content where you can post content.
    """


class IPost(IPostContent, ISilvaObject):
    """Posted content.
    """

    def get_creator():
        """Return post creator name.
        """

    def get_text():
        """Return post text content
        """

    def set_text(text):
        """Set post text content
        """


class IForum(IPostable):
    """Silva Forum is a collection of topics containing comments.
    """

    def add_topic(topic, anonymous=False):
        """ Add a topic
        """

    def topics():
        """ Return all topics (list)
        """


class ITopic(IPostable, IPost):
    """ A topic in a forum
    """

    def add_comment(title, text, anonymous=False):
        """ Add a comment.
        """

    def comments():
        """ Return all comments (list)
        """


class IComment(IPost, IContent):
    """ A single comment in a forum
    """
