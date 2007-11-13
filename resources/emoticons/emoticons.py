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
    for key, value in d.items():
        for subvalue in value:
            ret.append((key, subvalue))
    ret.sort(lambda a, b: cmp(len(b[1]), len(a[1])))
    return ret

def emoticons(text, imagedir):
    if imagedir.endswith('/'):
        imagedir = imagedir[:-1]
    for image, smiley in flatten_smileydata():
        smiley_html = '<img src="%s/%s" alt="%s" />' % (imagedir,
                                                        image,
                                                        get_alt_name(image))
        text = text.replace(smiley, smiley_html)
    return text

