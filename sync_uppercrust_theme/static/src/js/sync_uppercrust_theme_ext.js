(function () {
    'use strict';
    var website = odoo.website,
        qweb = odoo.qweb;
    // $(window).bind('scroll', function () {
    //     var topbar_el = $('.navbar-static-top');
    //     var scrollTop = $(window).scrollTop();
    //     if($('.master_background:first').length > 0){
    //         var top_height = $('.master_background:first').position().top + $('.master_background:first').height();
    //         if (!topbar_el.hasClass('fixed') && scrollTop > top_height){
    //             topbar_el.addClass('fixed');
    //             topbar_el.css({
    //                 top: '-100px',
    //             }).animate({
    //                 top: '0',
    //                 }, 500, function() {
    //             });
    //             $('.navbar-brand.logo img').addClass('clone_img');
    //             $('#top_menu li').addClass('clone_font');
    //             $('#top_menu').addClass('oe_cu_nev_back');
    //             $('#top_menu').css('margin-right', '0px');
    //             $('.navbar .container').css('margin', '0px 0px 0px 78px');
    //             $('ul.dropdown-menu').css('background-color', '#eaeaea');
    //             $('ul.dropdown-menu li.clone_font').addClass('fixed-menu');
    //
    //         } else {
    //             if(topbar_el.hasClass('fixed') && scrollTop < top_height){
    //                 topbar_el.removeClass('fixed').css('top','0px');
    //                 $('#top_menu').removeClass('oe_cu_nev_back');
    //                 $('#top_menu').css('margin-right', '10px');
    //                 $('.navbar-brand.logo img').removeClass('clone_img');
    //                 $('#top_menu li').removeClass('clone_font');
    //                 $('.navbar .container').css('margin', '25px 0px 0px 78px');
    //                 $('ul.dropdown-menu').css('background-color', '#FFF');
    //                 $('ul.dropdown-menu li.clone_font').removeClass('fixed-menu');
    //             }
    //         }
    //     }
    // });
})();

$(document).ready(function () {
    // $('#map_canvas').mapit();
    // $('#accordion').collapse({hide: true});
    $(".o_close").on('click', function (e) {
      $(this).parent().find('#inlineVideo').attr('src', '');
      $("#video_modal").modal('hide');
    });
    $("#video_modal").on('shown.bs.modal', function (e) {
        $(e.currentTarget).find('#inlineVideo').attr('src', e.relatedTarget.attributes['data-url'].value);
    });
    $('a.add-tab').parent().hide();
    $('a.add-tab-2').parent().parent().hide();
    $('.st-tabs li.active, .st-tabs .tab-pane.active').removeClass('active');
    _.each($('.st-tabs'), function (tab_el) {
        $(tab_el).children().find('li:first, .tab-pane:first').addClass('active')
    });
    $('.st-tabs-2 .panel-heading a').click(function () {
        if (!$(this).parents().eq(2).children('.panel-collapse').hasClass('in')) {
            $(this).closest('.st-tabs-2').find('.panel-collapse.in').removeClass('in');
            $(this).parent().children('.panel-collapse:first').addClass('in');
        }
        else {
            $(this).parent().children('.panel-collapse:first').removeClass('in');
        }
    });

    $('.post').addClass("hidebefore").viewportChecker();
    $('.post-start').viewportChecker({
        callbackFunction: function (elem, action) {
            setTimeout(function () {
                var odometer_el = $(elem).find('.odometer')
                odometer_el.html(odometer_el.attr('stop-counter'));
            }, 1000);
        }
    });
    $(".oe_fader").click(function () {
        var st_gallery = $(this).parent().parent();
        st_gallery.gallerie();
        if ($('.gallerie-overlay').length > 1) {
            $('.gallerie-overlay').css({'z-index': -10, 'top': '-1000px'});
            st_gallery.find('.gallerie-overlay').css({'z-index': 10, 'top': '0px'});
        }
    });
    $(".oe_fader a .fa-search-plus").click(function () {
        $('body').find('#oe_main_menu_navbar').css('display', 'none');
    });
    $('.gallery .oe_fader img').attr('style', '');
    _.each($('a#video_link'), function (video_el) {
        $(video_el).attr('href', '#video_modal')
    });

    if(document.querySelector('#wrapwrap').hasAttribute('js_class')){
        $(window).scroll(function(){
            if ($(window).scrollTop() > 0) {
               $('.navbar-static-top').addClass('fixed-header');
               $('main').addClass('fixed-header');
            }
            else {
               $('.navbar-static-top').removeClass('fixed-header');
               $('main').removeClass('fixed-header');
            }
        });
    }
});
