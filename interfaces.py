# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

from silva.core.interfaces import IContent, IContainer


class IPostable(IContainer):
    """Content where you can post content.
    """


class IPost(IContent):
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


class IComment(IPost):
    """ A single comment in a forum
    """
