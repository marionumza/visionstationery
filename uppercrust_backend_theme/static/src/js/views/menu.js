// odoo Menu inherit Open time has Children submenu add.
odoo.define('uppercrust_backend_theme.Menu', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var Menu = require('web.Menu');
    var UserMenu = require('web.UserMenu');
    var QuickMenu = require('uppercrust_backend_theme.QuickMenu');
    var GlobalSearch = require('uppercrust_backend_theme.global_search');
    var config = require('web.config');
    var session = require('web.session');

    var LogoutMessage = Widget.extend({
        template: 'LogoutMessage',
        events: {
            'click  a.oe_cu_logout_yes': '_onClickLogout',
            'click  .mb-control-close': '_onClickClose',
        },
        init: function (parent) {
            this._super(parent);
        },
        _onClickLogout: function (e) {
            var self = this;
            self.getParent()._onMenuLogout();
        },
        _onClickClose: function (e) {
            this.$el.remove();
        }
    });

    var MenuGlobalSearch = Widget.extend({
        template: 'menu.GlobalSearch',
        events: {
            'click  .oe_back_btn': '_closeGloblesearch',
            'click  ul.o_glonal_search_dropdown:not(.oe_back_btn)': '_onClickInside',
        },
        init: function (parent) {
            this._super(parent);
        },
        _closeGloblesearch: function (e) {
            e.preventDefault();
            e.stopPropagation();
            $(e.currentTarget).parents('.o_gb_search').removeClass('open');
        },
        _onClickInside: function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (e.offsetX < this.$('.o_glonal_search_dropdown')[0].offsetWidth) {
                $(e.currentTarget).parents('.o_gb_search').addClass('open');
            } else {
                $(e.currentTarget).parents('.o_gb_search').removeClass('open');
            }
        },
    });

    UserMenu.include({
        start: function () {
            // this._super.apply(this, arguments);
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                var $avatar = self.$('.oe_topbar_avatar');
                var avatar_src = session.url('/web/image', {
                    model: 'res.users',
                    field: 'image',
                    id: session.uid,
                });
                $avatar.attr('src', avatar_src);
                self.$el.on('click', 'li a.o_menu_logout', function (ev) {
                    ev.preventDefault();
                    return new LogoutMessage(self).appendTo(self.$el.closest('body'));
                });
            });
        },
    });

    Menu.include({
        open_menu: function (id) {
            this._super.apply(this, arguments);
            var $clicked_menu, $sub_menu, $sub_menu_count, $body, $parent_menu;

            // If has childmenu visible button
            $body = $('body');
            this.$sub_menus = this.$el.parents().find('.o_sub_menu_content');
            $clicked_menu = this.$el.add(this.$sub_menus).find('a[data-menu=' + id + ']');
            if (this.$sub_menus.has($clicked_menu).length) {
                $sub_menu = $clicked_menu.parents('.oe_secondary_menu');
                $sub_menu_count = $sub_menu;
            } else {
                $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + $clicked_menu.attr('data-menu') + ']');
                $sub_menu_count = $sub_menu.find('.ad_sub_menu');
            }

            // Show current sub menu
            this.$sub_menus.find('.oe_secondary_menu').hide();
            $sub_menu.show();

            // Main menu click time open child menu [start]
            $parent_menu = $('.menu_section').children('ul');
            $parent_menu.click(function () {
                var $has_click_menu = $(this).children('li').children('a').hasClass('oe_menu_toggler');
                if ($has_click_menu) {
                    $body.removeClass('nav-sm');
                    $('#menu_toggle').removeClass('active');
                }
                else {
                    $body.removeClass('nav-sm ad_open_childmenu ad_nochild');
                    $('#children_toggle').removeClass('active');
                    $('#menu_toggle').removeClass('active');
                }
            });
            this.$sub_menus.find('li').click(function () {
                var $click_child_menu = $(this).children('a').hasClass('oe_menu_leaf');
                if ($click_child_menu) {
                    $body.removeClass('nav-sm ad_open_childmenu ad_nochild');
                    $('#children_toggle').removeClass('active');
                    $('#menu_toggle').removeClass('active');
                    if ((config.device.size_class <= config.device.SIZES.XS) || (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))) {
                        $body.addClass('ad_full_view');
                    }
                }
            });

            this.$sub_menus.find('.oe_secondary_menu_section').click(function () {
                var $oe_secondary_menu_section = $(this).children('a').hasClass('oe_menu_leaf')
                if ($oe_secondary_menu_section) {
                    $body.removeClass('nav-sm ad_open_childmenu ad_nochild');
                    $('#children_toggle').removeClass('active');
                    $('#menu_toggle').removeClass('active');
                    if ((config.device.size_class <= config.device.SIZES.XS) || (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))) {
                        $body.addClass('ad_full_view');
                    }
                }
            });
            if ($('.o_main_content.ad_rightbar').hasClass('ad_open_search')) {
                this.call('local_storage', 'setItem', 'visible_search_menu', 'True');
            }
            // Hide/Show the Submenubar menu depending of the presence of sub-items
            $body.toggleClass('ad_nochild', !$sub_menu_count.children().length);
        },
        bind_menu: function () {
            var self = this;
            this._super.apply(this, arguments);
            new QuickMenu(self).appendTo(this.$el.parents('.o_web_client').find('.top_nav .ad_navbar'));
            this.$el.parents('.o_web_client').find('.oe_systray li.o_global_search').remove();
            new MenuGlobalSearch(self).appendTo(this.$el.parents('.o_web_client').find('.top_nav .o_quick_menu'));
            new GlobalSearch(self).appendTo(this.$el.parents('.o_web_client').find('.top_nav .o_gb_search ul'));
        },
    });
});