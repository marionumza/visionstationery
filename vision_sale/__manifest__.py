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

    'name': "Vision Sales",
    'summary': """Customised Sales for Vision Stationery""",
    'category': 'Sale',
    'version': '11.0.1',
        'description': """
Customised Sales for Vision Stationery
==================================================
    - last update: 27-APR-2019
    
        
    """,

    'author': "Alitec Pte Ltd",
    'depends': [
        'sale', 'stock', 'stock_request'
    ],
    'data': ['data/crm.team.csv',
             'data/server_action.xml',
             'views/sale.xml',
             'views/pricelist.xml',
             'views/warehouse.xml',
             'views/menu.xml'
    ],
}