odoo.define('sync_uppercrust_twitter.animation', function (require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var base = require('web_editor.base');
var animation = require('website.content.snippets.animation');
var website = require('website.website');
var Animation = require('website_twitter.animation');
// var snippets = require('website.snippets.editor');
// var options = require('web_editor.snippets.options');

var qweb = core.qweb;
var _t = core._t;
    
ajax.loadXML('/sync_uppercrust_twitter/static/src/xml/templates.xml', qweb);

animation.registry.twitter.include({
    render: function(data){
        var self = this;
        var timeline =  this.$target.find(".twitter_timeline");
        var tweets = [];
        $.each(data, function (e, tweet) {
            tweet.created_at = self.parse_date(tweet);
            tweet.text = self.parse_tweet(tweet);
            tweet.user.profile_image_url = tweet.user.profile_image_url.replace('_normal', '');
            tweets.push(qweb.render("website.Twitter.Tweet.Custom", {'tweet': tweet}));
        });

        if (!_.isEmpty(tweets)) {
            this.$scroller = $(qweb.render("website.Twitter.Scroller.Custom"));
            this.$scroller.appendTo(this.$target.find(".twitter_timeline"));
            var activated = 0;
            _.each(tweets, function(tweet){
             if (activated == 0){
                 self.$scroller.find("div[id^='scroller'] .carousel.carousel_twitter .carousel-inner").append(tweet.replace('st-tweet', 'st-tweet active'));
                 activated++;
             }else{self.$scroller.find("div[id^='scroller'] .carousel.carousel_twitter .carousel-inner").append(tweet)}
            });
        }
    },
});
    // options.registry.slider.include({
    //     start : function () {
    //         var self = this;
    //         this._super();
    //         if (this.$target.hasClass('carousel_twitter')){
    //             _.each(this.$el, function(control){
    //                 if($(control).attr('data-add_slide') == 'true')
    //                     $(control).hide();
    //                 if($(control).attr('data-remove_slide') == 'true')
    //                     $(control).hide();
    //             });
    //         }
    //     },
    // });
});
