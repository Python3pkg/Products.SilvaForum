# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
smileydata = {
    'angry.gif': (': x', ':x', ':-x', ':angry:'),
    'apprehension.gif': (': |', ':|', ':-|', ':apprehension:'),
    'arrow.gif': (':arrow:',),
    'confusion.gif': (': ?', ':?', ':-?', ':confusion:'),
    'cool.gif': ('8 )', '8)', '8-)', ':cool:'),
    'embarrassment.gif': (':oops:',),
    'exclamation.gif': (':!:',),
    'happy.gif': (': )', ':)', ':-)', ':D', ': D', ':-D', ':happy:'),
    'idea.gif': (':idea:',),
    'mad.gif': (':evil:',),
    'question.gif': (':?:',),
    'sad.gif': (': (', ':(', ':-(', ':sad:'),
    'shocked.gif': (':shocked:',),
    'surprised.gif': (': o', ':o', ':-o', ':surprised:'),
    'twisted.gif': (':twisted:',),
    'wink.gif': ('; )', ';)', ';-)', ':wink:'),
}

def get_alt_name(imgname):
    return smileydata[imgname][0]

def flatten_smileydata(d=smileydata):
    ret = []
    for key, value in list(d.items()):
        for subvalue in value:
            ret.append((key, subvalue))
    ret.sort(lambda a, b: cmp(len(b[1]), len(a[1])))
    return ret

def emoticons(text, imagedir):
    if imagedir.endswith('/'):
        imagedir = imagedir[:-1]
    textchunks = [text]
    for image, smiley in flatten_smileydata():
        newchunks = []
        for chunk in textchunks:
            if chunk.startswith('<img'):
                newchunks.append(chunk)
            elif smiley in chunk:
                smiley_html = '<img src="%s/%s" alt="%s" />' % (imagedir,
                                                               image,
                                                               get_alt_name(image))
                chunkparts = chunk.split(smiley)
                for part in chunkparts:
                    newchunks.append(part)
                    newchunks.append(smiley_html)
                newchunks.pop()
            else:
                newchunks.append(chunk)
        textchunks = newchunks
    return ''.join(textchunks)

