# Copyright (c) 2007-2008 Infrae. All rights reserved.
# See also LICENSES.txt
# SilvaForum
# Python

from zope.interface import Interface
from silva.core.interfaces import IContent, IContainer


class IPostableView(Interface):
    """Generic view interface on item where you can post.
    """

    def authenticate():
        """Unauthorized: should redirect you to the login page.
        """

class IForumView(IPostableView):
    """View for forum.
    """

class ITopicView(IPostableView):
    """View for a topic.
    """

class IPostable(IContent):
    """ Marker interface for content where you can post content.
    """

class IForum(IPostable):
    """ Silva Forum is a collection of topics containing comments

        see ITopic and IComment for (respectively) the topic and comment
        interfaces
    """
    def add_topic(topic):
        """ add a topic
        """

    def topics():
        """ return all topics (list)
        """

class ITopic(IPostable):
    """ a topic in a forum
    """
    def add_comment(comment):
        """ add a comment
        """

    def comments():
        """ return all comments (list)
        """

    def get_text():
        """ return the text content
        """

    def set_text(text):
        """ set the text content
        """

class IComment(IContent):
    """ a single comment in a forum
    """
    def get_text():
        """ return the text content
        """

    def set_text(text):
        """ set the text content
        """

