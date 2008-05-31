Copyright (c) 2007-2008 Infrae. All rights reserved.
See also LICENSE.txt

Meta::
  
  Valid for:        SilvaForum 0.1-beta-3 (SVN/Unreleased)
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

SilvaForum is an extension for Silva 2.x that provides a classic discussion
forum environment. Site visitors to create topics (subjects or questions) and
add comments to existing topics. SilvaForum can be integrated with OpenID
authentication and a CAPTCHA to prevent ‘spambots’ from attempting to post. 

Installating SilvaForum
-----------------------

See INSTALL.txt for installation instructions, plus how to activate the Silva
Forum stylesheet. 

Using SilvaForum
----------------

Visit the SMI (Silva Management Interface) to create a 'Silva Forum' object:
this will serve as the root of the forum. The public views of the Forum allow
(registered) clients to add topics (subjects) to the forum, and comments
(messages) to the topics. The topics and comments are accessible from the
SMI for editing and moderation purposes.

Access
------

Forums can be either exposed to the public, with authentication on the forms,
or they can only be viewed by authorized users.

Probably the forum is already viewable by the public. If not, go to the access
tab of the forum in the SMI and from the 'public view access restrictions'
choose the setting 'Anonymous' and click 'set restrictions'. This will allow
the public to see and navigate the forum, however if any form input is
submitted the user will be prompted for their login.

If the forum should only be viewed by authorized individuals, go to the access
tab in the SMI and from the 'public view access restrictions', choose the
setting 'Authorized', and click 'set restrictions'. This only allows authorized
users to access and view the forum and users will be prompted for login when
entering the forum.

Logging out with Internet Explorer
----------------------------------

Users using Internet Explorer have to explicitly logout with an unknown username
and password, otherwise, IE will keep the current user logged in.

Credits
-------

Many thanks to Bas Leeflang and the Bijvoet Center http://www.bijvoet-center.nl/ 
for the assignment to build the forum.

Thank you Mark James of http://www.famfamfam.com/ for the great icons, which
we used in the forum views!

Questions, remarks, etc.
------------------------

If you have questions, remarks, bug reports or fixes, please send an email
to info@infrae.com or todd@infrae.com.
