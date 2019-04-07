odoo.define('uppercrust_backend_theme.ChatManager', function (require) {
    "use strict";

    // var bus = require('bus.bus').bus;
    // var utils = require('mail.utils');
    // var config = require('web.config');
    // var Bus = require('web.Bus');
    var core = require('web.core');
    var session = require('web.session');
    // var time = require('web.time');
    var web_client = require('web.web_client');
    // var Class = require('web.Class');
    // var Mixins = require('web.mixins');
    // var ServicesMixin = require('web.ServicesMixin');
    var chat_manager = require('mail_base.base').chat_manager;
    // var chat_manager = require('mail.chat_manager');
    var _t = core._t;
    var _lt = core._lt;
    // var LIMIT = 25;
    // var preview_msg_max_size = 350;
    // var ODOOBOT_ID = "ODOOBOT";
    //
    // // Private model
    // //----------------------------------------------------------------------------------
    // var messages = [];
    // var channels = [];
    // var channels_preview_def;
    // var channel_defs = {};
    // var chat_unread_counter = 0;
    // var unread_conversation_counter = 0;
    // var emojis = [];
    // var emoji_substitutions = {};
    // var emoji_unicodes = {};
    // var starred_counter = 0;
    // var mention_partner_suggestions = [];
    // var canned_responses = [];
    // var commands = [];
    // var discuss_menu_id;
    // var global_unread_counter = 0;
    // var pinned_dm_partners = [];  // partner_ids we have a pinned DM with
    // var client_action_open = false;
    var ChatAction = core.action_registry.get('mail.chat.instant_messaging');
    ChatAction.include({
        init: function (parent, action, options) {
            this._super.apply(this, arguments);
            var channel_name = 'channel_sent';
            // Add channel Sent for show "Send message" button
            this.channels_show_send_button.push(channel_name);
            // Add channel Sent for enable "display_subject" option
            this.channels_display_subject.push(channel_name);
        },

        update_message_on_current_channel: function (current_channel_id, message) {
            var result = this._super.apply(this, arguments);
            var sent = current_channel_id === "channel_sent" && !message.is_sent;
            return sent || result;
        }
    });
    var chat_manager_super = _.clone(chat_manager);
    chat_manager.on_toggle_important_notification = function (data) {
        _.each(data.message_ids, function (msg_id) {
            var message = chat_manager.get_message(msg_id);
            if (message) {
                chat_manager.invalidate_caches(message.channel_ids);
                message.is_important = data.is_important;
                if (!message.is_important) {
                    chat_manager.remove_message_from_channel("channel_important", message);
                } else {
                    chat_manager.add_to_cache(message, []);
                    var channel_important = chat_manager.get_channel('channel_important');
                    channel_important.cache = _.pick(channel_important.cache, "[]");
                }
                chat_manager.bus.trigger('update_message', message);
            }
        });
    };
    chat_manager.on_toggle_no_channel_notification = function (data) {
        _.each(data.message_ids, function (msg_id) {
            var message = chat_manager.get_message(msg_id);
            if (message) {
                chat_manager.invalidate_caches(message.channel_ids);
                message.is_no_channel = data.is_no_channel;
                if (!message.is_no_channel) {
                    chat_manager.remove_message_from_channel("no_channel", message);
                } else {
                    chat_manager.add_to_cache(message, []);
                    var no_channel = chat_manager.get_channel('no_channel');
                    no_channel.cache = _.pick(no_channel.cache, "[]");
                }
                chat_manager.bus.trigger('update_message', message);
            }
        });
    };
    chat_manager.on_toggle_trash_notification = function (data) {
        _.each(data.message_ids, function (msg_id) {
            var message = _.findWhere(chat_manager.getMessages(), { id: msg_id });
            if (message) {
                chat_manager.invalidate_caches(message.channel_ids);
                message.is_trash = data.is_trash;
                if (!message.is_trash) {
                    chat_manager.remove_message_from_channel("channel_trash", message);
                } else {
                    chat_manager.add_to_cache(message, []);
                    var channel_trash = chat_manager.get_channel('channel_trash');
                    channel_trash.cache = _.pick(channel_trash.cache, "[]");
                    chat_manager.remove_message_from_channel("channel_inbox", message);
                }
                chat_manager.bus.trigger('update_message', message);
            }
        });
        if (data.channel_ids) {
            _.each(data.channel_ids, function (channel_id) {
                var channel = chat_manager.get_channel(channel_id);
                if (channel) {
                    channel.needaction_counter = Math.max(channel.needaction_counter - data.message_ids.length, 0);
                }
            });
        } else { // if no channel_ids specified, this is a 'mark all read' in the inbox
            _.each(channels, function (channel) {
                channel.needaction_counter = 0;
            });
        }
        // needaction_counter = Math.max(needaction_counter - data.message_ids.length, 0);
        // chat_manager.bus.trigger('update_needaction', needaction_counter);
    };
    chat_manager.on_toggle_star_notification = function (data) {
        var curr_starred_counter = chat_manager.get_starred_counter();
        var message_ids;
        if (data.starred) {
            message_ids = _.filter(data.message_ids, function (id) {
                var message = _.findWhere(chat_manager.getMessages(), {id: id});
                return !message || !message.is_starred;
            });
            curr_starred_counter += message_ids.length;
            chat_manager.set_starred_counter(curr_starred_counter);
        }else {
            message_ids = _.filter(data.message_ids, function (id) {
                var message = _.findWhere(chat_manager.getMessages(), {id: id});
                return !message || message.is_starred;
            });
            curr_starred_counter  = Math.max(curr_starred_counter - message_ids.length, 0);
            chat_manager.set_starred_counter(curr_starred_counter);
        }
        _.each(data.message_ids, function (msg_id) {
            var message = _.findWhere(chat_manager.getMessages(), { id: msg_id });
            if (message) {
                chat_manager.invalidate_caches(message.channel_ids);
                message.is_starred = data.starred;
                if (!message.is_starred) {
                    chat_manager.remove_message_from_channel("channel_starred", message);
                } else {
                    chat_manager.add_to_cache(message, []);
                    var channel_starred = chat_manager.get_channel('channel_starred');
                    channel_starred.cache = _.pick(channel_starred.cache, "[]");
                }
                chat_manager.bus.trigger('update_message', message);
            }
        });
        chat_manager.bus.trigger('update_starred', curr_starred_counter);
    };
    chat_manager.on_mark_as_seen_notification = function (data) {
        var curr_needaction_counter = chat_manager.get_needaction_counter();
        var message_ids;
        if (data.is_seen) {
            message_ids = _.filter(data.message_ids, function (id) {
                var message = _.findWhere(chat_manager.getMessages(), {id: id});
                return !message || !message.is_seen;
            });
            curr_needaction_counter  = Math.max(curr_needaction_counter - message_ids.length, 0);
            chat_manager.set_needaction_counter(curr_needaction_counter);
        }else {
            message_ids = _.filter(data.message_ids, function (id) {
                var message = _.findWhere(chat_manager.getMessages(), {id: id});
                return !message || message.is_seen;
            });
            curr_needaction_counter += message_ids.length;
            chat_manager.set_needaction_counter(curr_needaction_counter);
        }
        _.each(data.message_ids, function (msg_id) {
            var message = _.findWhere(chat_manager.getMessages(), { id: msg_id });
            if (message) {
                chat_manager.invalidate_caches(message.channel_ids);
                message.is_seen = data.is_seen;
                if (message.is_seen) {
                    chat_manager.bus.trigger('read_message', message);
                } else {
                    chat_manager.bus.trigger('unread_message', message);
                }
            }
        });
        if (data.channel_ids) {
            _.each(data.channel_ids, function (channel_id) {
                var channel = chat_manager.get_channel(channel_id);
                if (channel) {
                    channel.needaction_counter = Math.max(channel.needaction_counter - data.message_ids.length, 0);
                }
            });
        } else { // if no channel_ids specified, this is a 'mark all read' in the inbox
            _.each(channels, function (channel) {
                channel.needaction_counter = 0;
            });
        }
        chat_manager.bus.trigger('update_needaction', curr_needaction_counter);
    };
    chat_manager.on_partner_notification = function (data) {
        if (data.info === "unsubscribe") {
            var channel = chat_manager.get_channel(data.id);
            if (channel) {
                var msg;
                if (_.contains(['public', 'private'], channel.type)) {
                    msg = _.str.sprintf(_t('You unsubscribed from <b>%s</b>.'), channel.name);
                } else {
                    msg = _.str.sprintf(_t('You unpinned your conversation with <b>%s</b>.'), channel.name);
                }
                chat_manager.remove_channel(channel);
                chat_manager.bus.trigger("unsubscribe_from_channel", data.id);
                web_client.do_notify(_("Unsubscribed"), msg);
            }
        } else if (data.type === 'toggle_star') {
            chat_manager.on_toggle_star_notification(data);
        } else if (data.type === 'mark_as_read') {
            chat_manager.on_mark_as_read_notification(data);
        } else if (data.type === 'mark_as_unread') {
            chat_manager.on_mark_as_unread_notification(data);
        } else if (data.type === 'toggle_important') {
            chat_manager.on_toggle_important_notification(data);
        } else if (data.type === 'toggle_trash') {
            chat_manager.on_toggle_trash_notification(data);
        } else if (data.type === 'no_channel') {
            chat_manager.on_toggle_no_channel_notification(data);
        } else if (data.type === 'toggle_seen') {
            chat_manager.on_mark_as_seen_notification(data);
        } else if (data.info === 'transient_message') {
            chat_manager.on_transient_message_notification(data);
        } else if (data.type === 'activity_updated') {
            chat_manager.onActivityUpdateNodification(data);
        } else {
            chat_manager.on_chat_session_notification(data);
        }
    };
    chat_manager.get_channel_array = function(msg){
        return [ msg.channel_ids, 'channel_inbox', 'channel_starred', 'channel_sent', 'channel_important', 'no_channel', 'channel_seen', 'channel_trash' ];
    };
    chat_manager.get_properties = function(msg){
        return {
            is_starred: chat_manager.property_descr("channel_starred", msg, chat_manager),
            is_needaction: chat_manager.property_descr("channel_inbox", msg, chat_manager),
            is_sent: chat_manager.property_descr("channel_sent", msg, chat_manager),
            is_important: chat_manager.property_descr("channel_important", msg, chat_manager),
            no_channel: chat_manager.property_descr("no_channel", msg, chat_manager),
            is_seen: chat_manager.property_descr("channel_seen", msg, chat_manager),
            is_trash: chat_manager.property_descr("channel_trash", msg, chat_manager)
        };
    };
    chat_manager.property_descr = function (channel, msg, self) {
        return {
            enumerable: true,
            get: function () {
                return _.contains(msg.channel_ids, channel);
            },
            set: function (bool) {
                if (bool) {
                    chat_manager.add_channel_to_message(msg, channel);
                } else {
                    msg.channel_ids = _.without(msg.channel_ids, channel);
                }
            }
        };
    };
    chat_manager.set_channel_flags = function (data, msg) {
        msg.partner_ids = data.partner_ids;
        if (_.contains(data.needaction_partner_ids, session.partner_id)) {
            msg.is_needaction = true;
        }
        if (_.contains(data.starred_partner_ids, session.partner_id)) {
            msg.is_starred = true;
        }
        if (data.is_sent && _.contains(data.author_id, session.partner_id)) {
            msg.is_sent = true;
        }
        if (_.contains(data.important_partner_ids, session.partner_id)) {
            msg.is_important = true;
        }
        if (_.contains(data.seen_partner_ids, session.partner_id)) {
            msg.is_seen = true;
        }
        if (_.contains(data.trash_partner_ids, session.partner_id)) {
            msg.is_trash = true;
        }
        return msg;
    };
    chat_manager.get_domain = function (channel) {
        return (channel.id === "channel_sent")
            ? [['is_sent', '=', true],['author_id.user_ids', 'in', [session.uid]]]:
                (channel.id === "channel_important")
                    ? [['is_important', '=', true],
                        ['is_trash', '!=', true]]:
                    (channel.id === "no_channel")
                        ? [['is_no_channel', '=', true]]:
                        (channel.id === "channel_trash")
                            ? [['is_trash', '=', true]]
            : chat_manager_super.get_domain.apply(this, arguments);
    };
    chat_manager.remove_message_from_trash = function(channel_id, message) {
        message.channel_ids = _.without(message.channel_ids, channel_id);
        var channel = _.findWhere(chat_manager.get_channels(), { id: channel_id });
        _.each(channel.cache, function (cache) {
            cache.messages = _.without(cache.messages, message);
        });
    };
    chat_manager.toggle_important_status = function(message_id){
        var msg = chat_manager.get_message(message_id);
        return this._rpc({
            model: 'mail.message',
            method: 'set_message_important',
            args: [[message_id], !msg.is_important],
        });
    };
    chat_manager.mark_as_seen = function (message_ids, is_seen) {
        var is_sent = false;
        _.each(message_ids, function (msg_id) {
            var message = _.findWhere(chat_manager.getMessages(), {id: msg_id});
            if (_.contains(message.channel_ids, "channel_sent")) {
                is_sent = true;
            }
        });
        return this._rpc({
            model: 'mail.message',
            method: 'set_message_seen',
            args: [message_ids, is_seen],
            context: {'is_sent': is_sent},
        });
        // return MessageModel.call('set_message_seen', [message_ids, is_seen]);
    };
    chat_manager.mark_as_important = function(message_ids, is_important){
        // return MessageModel.call('set_message_important', [message_ids, is_important]);
        return this._rpc({
            model: 'mail.message',
            method: 'set_message_important',
            args: [message_ids, is_important],
        });
    };
    chat_manager.mark_as_trash = function(message_ids){
        if (message_ids.length) {
            // return MessageModel.call('set_message_trash', [message_ids]);
            return this._rpc({
                model: 'mail.message',
                method: 'set_message_trash',
                args: [message_ids],
            });
        } else {
            return $.when();
        }
    };
    chat_manager.is_ready.then(function () {
        // Add sent channel
        chat_manager.add_channel({
            id: "channel_sent",
            name: _lt("Sent"),
            type: "static"
        });
        chat_manager.add_channel({
            id: "channel_important",
            name: _lt("Important"),
            type: "static"
        });
        chat_manager.add_channel({
            id: "no_channel",
            name: _lt("No channel"),
            type: "static"
        });
        chat_manager.add_channel({
            id: "channel_trash",
            name: _lt("Trash"),
            type: "static"
        });
        return $.when();
    });
    return chat_manager;
});