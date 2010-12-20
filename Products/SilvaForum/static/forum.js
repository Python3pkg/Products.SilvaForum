

$(document).ready(function() {
    $('.dialog-opener').find('input').bind('click', function() {
        var opener = $(this);
        var dialog = $('.' + opener.attr('id') + '-dialog');
        opener.parent().slideUp("fast");
        dialog.slideDown("fast");
        return false;
    });
    $('.dialog-closer').bind('click', function() {
        var closer = $(this);
        var opener = $('#forum-'+ closer.attr('id').split('-')[1]);
        var dialog = $('.' + opener.attr('id') + '-dialog');
        dialog.slideUp("fast");
        opener.parent().slideDown("fast");
        return false;
    });

});
