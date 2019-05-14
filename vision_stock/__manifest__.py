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

    'name': "Vision Stock",
    'summary': """Customised Stock for Vision Stationery""",
    'category': 'Stock',
    'version': '11.0.1',
    'author': "Alitec Pte Ltd",
    'depends': [
        'sale', 'stock', 'stock_request'
    ],
    'data': ['data/server_action.xml',
             'views/warehouse.xml',
             'views/picking.xml',
             'views/stock_request.xml',
             'views/stock_rule.xml',
             'wizard/similar_pick_wizard.xml'
    ],
}