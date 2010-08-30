# Copyright (c) 2007-2010 Infrae. All rights reserved.
# See also LICENSES.txt
# $Id$

from Products.FileSystemSite.DirectoryView import registerDirectory
from silva.core import conf as silvaconf

registerDirectory('resources', globals())

silvaconf.extensionName('SilvaForum')
silvaconf.extensionTitle('Silva Forum')
