$(document).ready(function() {
    var txt_ids = $('textarea.st-txtarea');
    _.each(txt_ids, function(txt_id){
        $(txt_id).focus(function(){
            $(this).parent().find('label').css('opacity', 0);
        })
        .blur(function(){
            if ($(txt_id).val() == '')$(this).parent().find('label').css('opacity', 1);
        });
        $('.blog_post .st-img-single').addClass('bdr');
    });
    _.each($('.post-content-box .text'), function(postbox_content){
        $(postbox_content).html($(postbox_content).text());
    });

    $('#blog_right_column').find('section')
});