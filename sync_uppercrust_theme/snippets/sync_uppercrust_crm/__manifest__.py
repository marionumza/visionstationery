# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Uppercrust Contact Form",
    'description': """
                     Customized Uppercrust Theme: Contact snippet.
                   """,
    'version': "1.1",
    'author': "Synconics Technologies Pvt. Ltd.",
    'website': "www.synconics.com",
    'catagory': '',
    'depends': ['website_form','website_crm','sync_uppercrust_theme'],
    'data': [
        'static/src/xml/snippet.xml',
        'views/assets_registry.xml',
        'views/uppercrust_crm_templates.xml',
    ],
    'qweb': [],
    'active': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
