odoo.define('sync_uppercrust_blog.blog_animation', function(require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    require('web_editor.base');
    var animation = require('website.content.snippets.animation');

    var qweb = core.qweb;

    ajax.loadXML('/sync_uppercrust_blog/static/src/xml/templates.xml', qweb);

    animation.registry.s_blog = animation.Class.extend({
        selector: ".blog",
        start: function () {
            var self = this;
            var timeline = this.$target.find(".blog_timeline");
            ajax.jsonRpc('/blog_posts','call', {}).then(function(data) {
                self.$target.find(".blog_timeline").empty();
                if (data.error){
                    self.error(data);
                }
                else {
                    self.render(data);
                }
            });
        },
        render: function(data){
            var self = this;
            var timeline =  this.$target.find(".blog_timeline");
            var posts = [];
            $.each(data, function (e, blog_post) {
                blog_post.created_at = self.parse_date(blog_post);
                if (blog_post.bg_img && blog_post.bg_img.indexOf('website_blog') < 1){
                    blog_post.bg_img = 'data:image/jpeg;base64,' + blog_post.bg_img;
                }
                posts.push(core.qweb.render("website.Blog.Post", {'blog_post': blog_post}));
            });
            if (!_.isEmpty(posts)) {
                this.$postbox = $(core.qweb.render("website.Blog.PostBox"));
                this.$postbox.appendTo(timeline);
                _.each(posts, function(post){
                   self.$postbox.find("div[class^='blog-row']").append(post);
                });
            }
        },
        parse_date: function(blog_post) {
            if (_.isEmpty(blog_post.created_date)) return "";
            var v = blog_post.created_date.split(' ');
            return v[0].toString();
        },
    });
});