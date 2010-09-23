

$(document).ready(function() {
    $('.dialog-toggle').find('input').bind('click', function() {
        var button = $(this);
        var dialog = $('.' + button.attr('id') + '-dialog');
        button.hide("fast");
        dialog.show("fast");
        return false;
    });
});
