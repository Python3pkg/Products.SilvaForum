==========
SilvaForum
==========

What is it?
===========

SilvaForum is an extension for `Silva`_ that provides a classic
discussion forum environment. Site visitors can create topics
(subjects or questions) and add comments to existing
topics.


Using Silva Forum
=================

After enabling the Silva Forum extension you can create a *Silva
Forum* content in the Silva Management Interface: this will be the
forum. The public interface of the Forum allows site visitors to add
topics (subjects) to the forum, and comments (messages) to the
topics. The topics and comments are accessible from the management
interface by site editors for editing and moderation purposes.

Managing Access
===============

Consulting the forum
--------------------

By default, the forum, topic and comments are viewable by
unauthenticated people like any other Silva content. If you wish to
restrict this, you can use the default access restriction feature of
Silva to do so (located in the management interface, in the access tab).
For more information about this, please consult the Silva user
documentation.

Posting new topics and comments
-------------------------------

By default you need to be authenticated to be able to post a topic or
a comment.

For unauthenticated visitors, a link on a forum or a topic will let
them authenticate in order to be able to post.

A site manager can, per forum or per topic, authorize unauthenticated
people to post. This is configured in the management interface in
the settings screen of the properties tab). If this option is
activated, unauthenticated site visitors will be able to post new
topic or comments after filling in a Captcha.

The ``silva.pas.openid`` package can be installed in order to provide
authentication via OpenID. This authentication will be sufficient to let
site visitors post on forums and topics.

Another option, anonymous posting, can be activated by site managers
on the same screen as the unauthenticated posting. It will permit
authenticated visitors to hide their names on the topic or comment
they posted.

Notification
============

A site manager can, per forum or per topic, activate a subscription
feature. If activated, this will allow visitors, after subscription, to
receive notifications by email when a new comment is posted on a topic.

If you email is known (i.e. you filled it in in Silva, or it was provided
by your OpenID provider), you will have the possibility to directly
subscribe yourself to a topic when you post it, or to a topic when you
post a comment in it.

Of course people can cancel their subscription when they wish to.

This feature is provided by ``silva.app.subscriptions``. To have it,
you need to enable subscriptions for the forum, just like you would
do for other Silva content. For more information about the
subscription feature, you can consult the Silva user documentation.

Credits
=======

Many thanks to Bas Leeflang and the Bijvoet Center
http://www.bijvoet-center.nl/ for the assignment to build the forum.

Thank you Mark James of http://www.famfamfam.com/ for the great icons,
which we used in the forum views! And the theme of JForum for emoticons
icons.

For Silva 2.2/2.3 the forum was refactored and vastly improved, with
the generous help of the Schweizerischer Erdbebendienst (SED, or Swiss
Seismological Service) and ETH Zurich: http://www.seismo.ethz.ch/

Code repository
===============

You can find the code of this extension in Git:
https://github.com/silvacms/Products.SilvaForum

.. _Silva: http://silvacms.org
