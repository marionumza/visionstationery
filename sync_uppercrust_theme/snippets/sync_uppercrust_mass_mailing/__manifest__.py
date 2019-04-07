# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': "Uppercrust Newsletter",
    'description': """
                     Customized Uppercrust Theme: Newsletter snippet.
                   """,
    'version': "1.1",
    'author': "Synconics Technologies Pvt. Ltd.",
    'website': "www.synconics.com",
    'catagory': '',
    'depends': ['website_mass_mailing', 'sync_uppercrust_theme'],
    'data': [
        'static/src/xml/snippet.xml',
        'views/assets_registry.xml'
    ],
    'qweb': [],
    'active': True,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
