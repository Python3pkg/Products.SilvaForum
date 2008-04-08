# Copyright (c) 2007 Infrae. All rights reserved.
# See also LICENSES.txt
# SilvaForum
# Python

from zope.interface import Interface


class IForumSecurityPolicy(Interface):
    """ This defines if the user have the right to post or not.
    """

    def can_add_topic():
        """Return true if the user is authorized to add a topic.
        """

    def can_add_post():
        """Return true if the user is authorized to add a post.
        """

class IPostable(Interface):
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

class IComment(Interface):
    """ a single comment in a forum
    """
    def get_text():
        """ return the text content
        """

    def set_text(text):
        """ set the text content
        """

