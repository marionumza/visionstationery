odoo.define('sync_uppercrust_blog.website_chatter', function(require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');

var qweb = core.qweb;

var PortalChatter = require('portal.chatter').PortalChatter;

/**
 * Extends Frontend Chatter to moddified styles
 */
PortalChatter.include({
    _loadTemplates: function(){
        return $.when(this._super(), ajax.loadXML('/sync_uppercrust_blog/static/src/xml/portal_chatter.xml', qweb));
    },
});

});
