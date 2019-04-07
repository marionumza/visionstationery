$(document).ready(function(){
    var subscribe_els = $('input.js_subscribe_email');
    // if ($(subscribe_el).val() == '')$(subscribe_els).parent().find('label').css('opacity', 1);
    _.each(subscribe_els, function(subscribe_el){
        $(subscribe_el).focus(function(){
            $(this).parent().find('label').css('opacity', 0);
        })
        .blur(function(){
            if ($(subscribe_el).val() == '')$(this).parent().find('label').css('opacity', 1);
        });
    });
});