##############################################################################
#
# Copyright (c) 2019 Alitec Pte Ltd All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract support@modoolar.com
#
##############################################################################
{

    'name': "Vision Master",
    'summary': """Customised Master Data for Vision Stationery""",
    'category': 'Vision',
    'version': '11.0.1.1',
    'author': "Alitec Pte Ltd",
    'depends': [
        'sale',
    ],
    'data': ['security/ir.model.access.csv',
             'views/portal_product.xml'
    ],
}