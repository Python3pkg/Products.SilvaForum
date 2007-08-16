def initialize(context):
    from Products.Silva.fssite import registerDirectory
    registerDirectory('emoticons/smilies', globals())
