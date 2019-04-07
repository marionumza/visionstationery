odoo.define('sync_uppercrust_mass_mailing.ext', function (require) {
'use strict';
    var core = require('web.core');
    var animation = require('website.content.snippets.animation');
    animation.registry.subscribe.include({
        // selector: ".js_subscribe",
        start: function (editable_mode) {
            var self = this;
            self._super();
            var subscribe_el = this.$target.parent().find('label');
            if($(subscribe_el.value && $(subscribe_el).value.length > 0))
                subscribe_el.css('opacity', 0);
        }
    });
});
