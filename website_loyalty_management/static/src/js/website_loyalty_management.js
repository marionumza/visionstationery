odoo.define('website_loyalty_management.website_loaylty_management', function(require) {
    var ajax = require('web.ajax');
    $(document).ready(function() {
        if (typeof $('#auto_remove').prev().attr('href') == 'string' &&
            $('#auto_remove').prev().data('virtual_source') == 'wk_website_loyalty') {
            location.href = $('#auto_remove').prev().attr('href');
        }

        var html = $('#cart_total').html()
        setInterval(function() {
            if ($('#cart_total').html() != html) {
                html = $('#cart_total').html()
                $("#sale_order_can_make_points").addClass('bg-primary');
                var wk_auto_remove_parent = $('.wk_auto_remove').parent();
                if (typeof wk_auto_remove_parent.attr('href') == 'string' &&
                    wk_auto_remove_parent.data('virtual_source') == 'wk_website_loyalty') {
                    location.href = wk_auto_remove_parent.attr('href')
                }
                setTimeout(function() {
                    $("#sale_order_can_make_points").load(location.href + " #sale_order_can_make_points");
                    $("#sale_order_can_make_points").removeClass('bg-primary');
                    $("#span_is_virtual").load(location.href + " #span_is_virtual");

                }, 200);
            }

        }, 1000);

        function model_show() {
            $('#modal_confimation').modal('show').on('shown.bs.modal', function() {
            }).on('hidden.bs.modal', function() {
                $('modal-backdrop fade in').remove();
                $('#modal_confimation').remove();
                $(this).remove();
            });
        }

        $('._o_loyality_confimation').on('click', function() {
            var $el = $(this);
            ajax.jsonRpc('/loyalty/confirmation/', 'call', {})
            .then(function(response) {
                var $modal = $(response);
                var $modal = $(response.toString());
                $modal.appendTo($('._o_loyality_confimation').parent().parent())
                .modal('show')
                .on('hidden.bs.modal', function() {
                    $(this).remove();
                });

            });
        });
        $('._o_link_redeem_rule').on('click', function() {
            $('#redeem_rule_modal').appendTo('body').modal('show').on('shown.bs.modal', function() {
                $('#modal_confimation').hide();
            });
        });

        // $('.one_time_redeem_example').on('click',
        //     function() {
        //         $(this).parent().parent().find('.one_time_redeem_example_div').show({
        //             direction: "left"
        //         }, 500);
        //     });
        // $('.partial_redeem_example').on('click',
        //     function() {
        //         $(this).parent().parent().find('.partial_redeem_example_div').show({
        //             direction: "right"
        //         }, 500);
        //     });
        // $(".one_time_redeem_example_div").delegate("._o_one_time_redeem_policy_example_div_close", "click", function() {
        //     $('.one_time_redeem_example_div').hide({
        //         direction: "right"
        //     }, 500);
        // });
        // $(".partial_redeem_example_div").delegate("._o_partial_redeem_example_div_close", "click", function() {
        //     $('.partial_redeem_example_div').hide({
        //         direction: "left"
        //     }, 500);
        // });

    });
});
