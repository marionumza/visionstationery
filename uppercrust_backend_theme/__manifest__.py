# -*- coding: utf-8 -*-

{
    'name': 'Uppercrust Backend Theme',
    'category': "Themes/Backend",
    'version': '1.2',
    'summary': 'Fully responsive Uppercrust Backend Theme is available in v9, v10, v11, v12. Kindly contact us to buy it in various versions',
    'description': 'Fully responsive Uppercrust Backend Theme is available in v9, v10, v11, v12. Kindly contact us to buy it in various versions',
    'author': "Synconics Technologies Pvt. Ltd.",
    'depends': ['web_planner'],
    'website': 'www.synconics.com',
    'data': [
        'data/theme_data.xml',
        'security/global_search_security.xml',
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/webclient_templates.xml',
        'views/global_search_config_view.xml',
        'wizard/global_search_batch_wizard_view.xml',
        'views/global_search_config_batch_view.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'images': [
        'static/description/main_screen.jpg',
        'static/description/uppercrust_screenshot.jpg',
    ],
    'pre_init_hook': 'pre_init_check',
    'price': 449.0,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'bootstrap': True,
    'application': True,
    'license': 'OPL-1',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: