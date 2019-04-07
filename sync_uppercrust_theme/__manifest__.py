# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Uppercrust Theme',
    'description': 'Customized Uppercrust Theme',
    'version': "1.1",
    'author': "Synconics Technologies Pvt. Ltd.",
    'website': "www.synconics.com",
    'category': 'Theme/Corporate',
    'depends': ['website', 'theme_default'],
    'data': [
        'views/theme_uppercrust_snippets.xml',
        'views/theme_uppercrust_templates.xml',
    ],
    'images': [
        'static/description/main_screen.jpg',
        'static/description/uppercrust_screenshot.jpg',
    ],
    'price': 75,
    'currency': 'EUR',
    'live_test_url': 'http://uppercrust-default-theme-v11.synconics.com',
    'active': True,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
