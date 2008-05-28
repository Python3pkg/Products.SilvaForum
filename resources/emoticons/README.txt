Copyright (c) 2007-2008 Infrae. All rights reserved.
See also LICENSE.txt

Meta::

  Valid for:        emoticons 0.1
  Author:           Todd Matsumato, Guido Wesdorp
  Email:            todd@infrae.com
  Last author:      $Author: guido $
  SVN Revision:     $Date: 2007-08-10 13:17:03 +0200 (Fri, 10 Aug 2007) $
  Last modified:    $Rev: 25417 $


Emoticons library
=================

What is it?
-----------

Emoticons is a small library (well, currently anyway ;) with functionality to
replace plain-text smileys to image tags. It is written by Infrae for the SilvaForum
product, but can easily be used seperately. It provides a single function,
'emoticons.emoticons()', that receives 2 arguments, the first of which is the text
to replace the emoticons in, the second a path to where the emoticons reside.

Currently the file names are hard-coded into the emoticons lib, hopefully this will
change in due time.

Installing
----------

Just place the package in a place where Python can find it (e.g.
/usr/lib/python<version>/site-packages) or add the parent path of the package to
$PYTHONPATH.

License issues
--------------

The images used are (c) JForum Team, see LICENSE_JFORUM.txt for the license
(which is BSD-style, just like the package itself).

Questions, remarks, etc.
------------------------

If you have questions, bug reports, patches, or remarks, please send an email to
todd@infrae.com.

