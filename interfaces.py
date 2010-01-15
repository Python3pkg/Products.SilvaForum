# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

from silva.core.interfaces import IContent


class IPostable(IContent):
    """ Marker interface for content where you can post content.
    """


class IForum(IPostable):
    """ Silva Forum is a collection of topics containing comments

        see ITopic and IComment for (respectively) the topic and comment
        interfaces
    """

    def add_topic(topic, anonymous=False):
        """ Add a topic
        """

    def topics():
        """ Return all topics (list)
        """


class ITopic(IPostable):
    """ A topic in a forum
    """

    def add_comment(title, text, anonymous=False):
        """ Add a comment.
        """

    def comments():
        """ Return all comments (list)
        """

    def get_text():
        """ Return the text content
        """

    def set_text(text):
        """ Set the text content
        """


class IComment(IContent):
    """ A single comment in a forum
    """

    def get_text():
        """ Return the text content.
        """

    def set_text(text):
        """ Set the text content.
        """

