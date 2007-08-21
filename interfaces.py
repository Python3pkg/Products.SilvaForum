from zope.interface import Interface

class IForum(Interface):
    """ Silva Forum is a collection of topics containing comments

        see IThread and IComment for (respectively) the topic and comment
        interfaces
    """
    def add_thread(thread):
        """ add a thread
        """

    def threads():
        """ return all threads (list)
        """

class IThread(Interface):
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

