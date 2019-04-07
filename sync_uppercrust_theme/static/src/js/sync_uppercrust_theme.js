odoo.define('sync.uppercrust.theme', function (require) {
    'use strict';
    var ajax = require('web.ajax');
    var core = require('web.core');
    var base = require('web_editor.base');
    var Dialog = require('web.Dialog');
    var animation = require('website.content.snippets.animation');
    var options = require('web_editor.snippets.options');
    var widget = require('web_editor.widget');
    var editor = require('web_editor.editor');
    var rte = require('web_editor.rte');

    var _t = core._t;
    var qweb = core.qweb;

    ajax.loadXML('/sync_uppercrust_theme/static/src/xml/templates.xml', qweb);

    widget.MediaDialog.include({
        start: function () {
            var self = this;
            var res = this._super.apply(this, arguments);;
            $(self.media).hasClass('magniflier') ? self.$el.find('.well').before('<div class="text-center text-danger mt16">Magnify effect best viewed with image resolution 2200 x 1100 pixels.</div>') : false;
            return res;
        },
        save: function () {
            var self = this;
            this._super()
            var element = this.media;
            if (element.getAttribute('data-toggle') == 'gallery') {
                element.setAttribute('style', '');
                var st_gallery = $(element).parent();
                _.each(st_gallery.find('a'), function(anchor){
                    $(anchor).attr({'href': element.src});
                });
                _.each(st_gallery.find('img'), function(img){
                    $(img).attr({'src': element.src});
                });
            }
        }
    });
    widget.LinkDialog.include({
        start: function () {
            this._super();
        },
        save: function() {
            this._super();
            if(this.data.className == "hideme"){
                var anchor_el = $(this.data.range.ec);
                anchor_el.attr('data-cke-saved-href', anchor_el.attr('href'));
                anchor_el.attr('data-url', anchor_el.attr('href'));
                this.trigger('saved');
            }
        }
    });
    var ProgressbarDialog = Dialog.extend({
        template: 'uppercrust_theme.dialog.progressbar',
        dialog_title: _t('Customize Progress'),
        init: function (parent, title, pbar) {
            this.pbar = pbar;
            this._super(parent, {
                title: title,
                size: "medium",
                buttons: [{
                    text: _t("Save"),
                    close: true,
                    classes: "btn-primary",
                    click: this._doSave.bind(this),
                }, {
                    text: _t("Cancel"),
                    close: true,
                    classes: "btn-primary",
                    click: this._doCancel.bind(this),
                }],
            });
        },
        start: function () {
            var self = this;
            this._super();
            var res = self._getData($(this.pbar).find('div.progress-bar'));
            this.$el.find('input#pbar-color')[0].value = res['bg_color'];
            this.$el.find('input#pbar-perc')[0].value = res['perc_val'];
            this.$el.find('input#pbar-time')[0].value = res['pbar-time'];
        },
        _doSave: function () {
            var self = this;
            var colorval = this.$el.find('input#pbar-color')[0].value;
            var percval = this.$el.find('input#pbar-perc')[0].value;
            var timeval = this.$el.find('input#pbar-time')[0].value;
            var pbar_el = $(this.pbar).find('div.progress-bar');
            pbar_el.removeClass(function (index, css) {
                return (css.match(/\bbar-\S+/g) || []).join(' ')
            });
            pbar_el.attr({
                'data-pro-bar-percent': percval,
                'data-pro-bar-delay': timeval,
                'title': percval + "%"
            }).css({'background-color': colorval, 'width': percval + "%"}).addClass('bar-' + percval);
            // $(this.counter).attr({'stop-counter': this.$el.find('input#stop-counter')[0].value});
            // this.$el.find('.oe_cu_counter_model').removeClass('in')
            // this.$el.find('.oe_cu_counter_model').hide();
            this.destroy();
        },
        _doCancel: function () {
            this.destroy();
        },
        _getData: function (pbar) {
            var result = {};
            result['perc_val'] = pbar.attr('data-pro-bar-percent');
            result['bg_color'] = pbar.css('background-color');
            result['pbar-time'] = pbar.attr('data-pro-bar-delay');
            return result;
        }
    });
    var CounterDialog = Dialog.extend({
        template: 'uppercrust_theme.dialog.counter',
        dialog_title: _t('Customize Counter'),
        init: function (parent, title, counter) {
            this.counter = counter;
            this._super(parent, {
                title: title,
                size: "medium",
                buttons: [{
                    text: _t("Save"),
                    close: true,
                    classes: "btn-primary",
                    click: this._doSave.bind(this),
                }, {
                    text: _t("Cancel"),
                    close: true,
                    classes: "btn-primary",
                    click: this._doCancel.bind(this),
                }],
            });
        },
        start: function () {
            var self = this;
            this._super()
            this.$el.find('.oe_cu_counter_model').show();
            this.$el.find('.oe_cu_counter_model').addClass('in')
            var res = self._getData($(this.counter));
            this.$el.find('input#stop-counter')[0].value = res['stop_counter'];
        },
        _doSave: function () {
            var self = this;
            $(this.counter).attr({'stop-counter': this.$el.find('input#stop-counter')[0].value});
            this.$el.find('.oe_cu_counter_model').removeClass('in')
            this.$el.find('.oe_cu_counter_model').hide();
            this.destroy();
        },
        _doCancel: function () {
            this.$el.find('.oe_cu_counter_model').removeClass('in')
            this.$el.find('.oe_cu_counter_model').hide();
            this.destroy();
        },
        _getData: function (counter) {
            var result = {};
            result['stop_counter'] = counter.attr('stop-counter');
            return result;
        }
    });
    options.registry.s_title_hr = options.Class.extend({
        start: function () {
            this._super();
            this.$target.attr("contentEditable", true);
        },
        align: function (previewMode, value, $li) {
            this.$target.attr('align', value);
        }
    });
    animation.registry.s_references = animation.Class.extend({
        selector: ".s_references",
        start: function () {
            var self = this;
            this._super();
            if (this.$target.hasClass('carousel_testimonial')) {
                _.each(this.$el, function (control) {
                    if ($(control).attr('data-add_slide') == 'true')
                        $(control).find('a').text('Add Testimonial');
                    if ($(control).attr('data-remove_slide') == 'true')
                        $(control).find('a').text('Remove Testimonial');
                });
            }
        },
        add_slide: function () {
            var self = this;
            var cycle = this.$inner.find('.item').length;
            var $active = this.$inner.find('.item.active, .item.prev, .item.next').first();
            var index = $active.index();
            this.$target.find('.carousel-control, .carousel-indicators').removeClass("hidden");
            this.$indicators.append('<li data-target="#' + this.id + '" data-slide-to="' + cycle + '"></li>');

            var $snippets = false;
            if (this.$target.hasClass('carousel_testimonial'))
                var $snippets = this.buildingBlock.$snippets.find('.oe_snippet_body.carousel_testimonial');
            else
                var $snippets = this.buildingBlock.$snippets.find('.oe_snippet_body.carousel');

            var point = 0;
            var selection;
            var className = _.compact(this.$target.attr("class").split(" "));
            $snippets.each(function () {
                var len = _.intersection(_.compact(this.className.split(" ")), className).length;
                if (len > point) {
                    point = len;
                    selection = this;
                }
            });
            var $clone = $(selection).find('.item:first').clone();
            $clone.removeClass('active').insertAfter($active);
            setTimeout(function () {
                self.$target.carousel().carousel(++index);
                self.rebind_event();
            }, 0);

            var bg = this.$target.data("snippet-option-ids").background;
            if (!bg) return $clone;

            var $styles = bg.$el.find("li[data-value]:not(.oe_custom_bg)");
            var styles_index = $styles.index($styles.filter(".active")[0]);
            $styles.removeClass("active");
            var $select = $($styles[styles_index >= $styles.length - 1 ? 0 : styles_index]);
            $select.addClass("active");
            $clone.css("background-image", $select.data("src") ? "url('" + $select.data("src") + "')" : "");
            $clone.addClass($select.data("value") || "");
            return $clone;
        }
    });
    animation.registry.video = animation.Class.extend({
        selector: ".st-video",
        start: function () {
            var self = this;
            var anchor_el = this.$el.find('a#video_link')
            var editor_enable = $('body').hasClass('editor_enable');
            if(editor_enable){
                anchor_el.attr('href', anchor_el.attr('data-url'));
                anchor_el.attr('data-cke-saved-href', anchor_el.attr('data-url'));
                this.$el.find('.video_container a').addClass('hideme');
                $('.glass').remove();
            }else{
                if (anchor_el.length > 0 && self.check_str(anchor_el.attr('data-url'))){
                    var youtube_parser = self.youtube_parser(anchor_el.attr('data-url'));
                    anchor_el.attr('data-url', 'https://www.youtube.com/v/' + self.youtube_parser(anchor_el.attr('data-url')));
                    anchor_el.attr('href', '#video_modal');
                    anchor_el.attr('data-cke-saved-href', '#video_modal');
                }
                this.$el.find('.video_container a').removeClass('hideme');
            }
        },
        check_str: function(str) {
            var regexp = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
               return regexp.test(str);
        },
        youtube_parser: function(url) {
            var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*/;
            var match = url.match(regExp);
            return (match&&match[7].length==11)? match[7] : false;
        }
    });
    options.registry.s_video = options.registry.marginAndResize.extend({
        start: function () {
            this._super();
            this.save();
        },
        save: function () {
            var self = this;
            this.buildingBlock.parent.rte.historyRecordUndo(this.$target);
        }
    });
    options.registry.s_progressbar = options.Class.extend({
        start: function () {
            this._super();
            this.$target.attr("contentEditable", false);
        },
        _onCustomizeButtonClicked: function (pbar_el) {
            var self = this;
            var title = _.str.sprintf(_t('Customize Progress'));
            new ProgressbarDialog(self, title, pbar_el).open();
        },
        customize: function (type) {
            var self = this;
            if (!type) self._onCustomizeButtonClicked(self.$target);
        }
    });
    options.registry.s_photo_gallery = options.Class.extend({
        start: function () {
            var def = this._super.apply(this, arguments);
            this.$target.attr("contentEditable", true);
            return def;
        },
        _addImage: function (gallery_el) {
            $(gallery_el).find('.oe_gallery_block').append($(core.qweb.render('web_editor.gallery.image', {})));
        },
        images_add: function (type) {
            var self = this;
            if (!type) {
                if (self.$target.find('.oe_gallery_block div').hasClass('hidden')) {
                    self._addImage(self.$target);
                } else {
                    self.$target.find('.oe_gallery_block div').addClass('hidden')
                    self._addImage(self.$target);
                }
            }
        },
    });
    options.registry.s_counter = options.Class.extend({
        start: function () {
            var self = this;
            this._super();
            this.$target.attr("contentEditable", false);
            // this.$target.closest('body').find('.cu-counter a').on("click", function (ev) {
            //     self._onCustomizeButtonClicked(ev);
            // })
        },
        _onCustomizeButtonClicked: function (counter_el) {
            var self = this;
            var title = _.str.sprintf(_t('Customize Counter'));
            new CounterDialog(self, title, counter_el).open();
        },
        customize: function (type) {
            var self = this;
            if (!type) self._onCustomizeButtonClicked(self.$target);
        }
    });
    options.registry.s_htabs_add = options.Class.extend({
        start: function () {
            var def = this._super.apply(this, arguments);
            this.$target.attr("contentEditable", true);
            return def;
        },
        _addTab: function () {
            var self = this;
            var lists = this.$('.o_htab_ul').children();
            var tab_content = this.$('div.tab-content');
            var tab_id = new Date().valueOf();
            $(lists).last('li').before('<li><a data-toggle="tab" href="#tab_' + tab_id + '">New Tab</a></li>');
            $(tab_content).append('<div role="tabpanel" class="tab-pane" id="tab_' + tab_id + '"><p>Tab : Body </p></div>');
            self._doSave();
        },
        add_tab: function (type) {
            var self = this;
            if (!type) {
                if (self.$target.find('.o_htab_info').hasClass('hidden')) {
                    self._addTab();
                } else {
                    self.$target.find('.o_htab_info').addClass('hidden')
                    self._addTab();
                }

            }
        },
        _doSave: function () {
            var self = this;
            this.buildingBlock.parent.rte.historyRecordUndo(this.$target);
        }
    });
    options.registry.s_vtabs_add = options.Class.extend({
        start: function () {
            var def = this._super.apply(this, arguments);
            this.$target.attr("contentEditable", true);
            return def;
        },
        _addTab: function () {
            var lists = this.$('.o_tab_container');
            var tab_id = new Date().valueOf();
            var options = {'action_href': '#collapse' + tab_id, 'action_id': 'collapse' + tab_id}
            $(lists).last('div.panel.panel-default').before($(core.qweb.render('web_editor.tab.style2', {widget: options})));
            self._doSave();
        },
        add_tab: function (type) {
            var self = this;
            if (!type) {
                if (self.$target.find('.o_tab_info').hasClass('hidden')) {
                    self._addTab();
                } else {
                    self.$target.find('.o_tab_info').addClass('hidden')
                    self._addTab();
                }

            }
        },
        _doSave: function () {
            var self = this;
            this.buildingBlock.parent.rte.historyRecordUndo(this.$target);
        }
    });
    animation.registry.s_progressbar = animation.Class.extend({
        selector: ".s_progressbar",
        start: function () {
            this._super();
            _.each($('.progress-bar'), function (pbar) {
                $(pbar).removeClass(function (index, css) {
                    return (css.match(/(animated{0,8})/g) || []).join(' ')
                })
            });
            _.each($('.post.hidebefore'), function (animate_post) {
                $(animate_post).removeClass('hidebefore')
            });
        }
    });
    animation.registry.s_team_member = animation.Class.extend({
        selector: ".s_team_member",
        start: function () {
            var def = this._super.apply(this, arguments);
            this.$target.attr("contentEditable", true);
            if(!this.$el.closest('section').hasClass('s_team_member_section')){
                this.$el.closest('section').addClass('s_team_member_section');
            }
            return def;
        },
    });
    animation.registry.s_well_inherit = animation.Class.extend({
        selector: ".s_well",
        start: function () {
            var def = this._super.apply(this, arguments);
            this.$target.attr("contentEditable", true);
            if(!this.$el.closest('section').hasClass('s_well_box')){
                this.$el.closest('section').addClass('s_well_box');
            }
            return def;
        },
    });

    // editor.Class.include({
    //     save: function () {
    //         var def = this._super.apply(this, arguments)
    //         $('.post').each(function(ev){
    //             $(this).removeClass($(this).data('vp-add-class'));
    //         });
    //         // alert(this.rte.editable().find('.s_team_member').closest('section').length)
    //         // this.rte.editable().find('.s_team_member').closest('section').addClass('s_team_member_section')
    //         return def;
    //     },
    // });
});
