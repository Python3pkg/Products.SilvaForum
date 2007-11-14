Copyright (c) 2007 Infrae. All rights reserved.
See also LICENSE.txt

Meta::
  
  Valid for:        SilvaForum 0.1-beta-2 (SVN/Unreleased)
  Author:           Todd Matsumoto, Guido Wesdorp
  Email:            todd@infrae.com
  Last author:      $Author$
  SVN Revision:     $Date$
  Last modified:    $Rev$

==========
SilvaForum
==========

What is it?
-----------

SilvaForum is a forum (or Bulletin Board System) for the Silva CMS. It allows
registered visitors of a Silva site to create topics (subjects or questions)
and comment on existing topics.

Installating SilvaForum
-----------------------

See INSTALL.txt for installation instructions, plus how to activate the Silva
Forum stylesheet. 

Using SilvaForum
----------------

Visit the SMI (Silva Management Interface) to create a 'Silva Forum' object:
this will serve as the root of the forum. The public views of the Forum allow
(registered) clients to add topics (topics) to the forum, and comments
(messages) to the topics. The topics and comments are accessible from the
SMI for moderation and maintenance purposes.

Authentication can be configured for the public view of the forum by going to
the SMI 'access' tab. 

if you want viewable to public but can't enter text set anonymous.

if you want to be not viewable to unauthorized set below
In the pulldown menu for 'public view access restrictions'
choose the setting 'Authenticated' and click 'set restriction'. Then only
authenticated users will be able to access the forum.

Logging out with Internet Explorer
----------------------------------

Users using Internet Explorer have to explicitly logout with an unknown username
and password, otherwise, IE will keep the current user logged in.

Thanks
------

Thank you Bas Leeflang and the Bijvoet Center http://www.bijvoet-center.nl/ for
the assignment to build the forum.

Thank you Mark James of http://www.famfamfam.com/ for the great icons, which
we used in the forum views!

Questions, remarks, etc.
------------------------

If you have questions, remarks, bug reports or fixes, please send an email
to info@infrae.com or todd@infrae.com.
