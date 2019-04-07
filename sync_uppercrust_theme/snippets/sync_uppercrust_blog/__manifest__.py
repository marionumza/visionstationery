# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Uppercrust Blog",
    'description': """
                    Customized Uppercrust Theme: Blog snippet.
                   """,
    'version': "1.1",
    'author': "Synconics Technologies Pvt. Ltd.",
    'website': "www.synconics.com",
    'catagory': '',
    'depends': ['website_blog','sync_uppercrust_theme'],
    'data': [
        'static/src/xml/snippet.xml', 
        'static/src/xml/theme.xml',
        'views/assets_registry.xml',
        'views/uppercrust_blog_templates.xml',
        'views/blog_view.xml'
    ],
    'active': True,
    'installable': True,
    'qweb': [
        'static/src/xml/chatter_message.xml',
        'static/src/xml/portal_chatter.xml',
        'static/src/xml/templates.xml',
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
