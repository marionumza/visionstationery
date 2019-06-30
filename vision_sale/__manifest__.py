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
    'version': '11.0.1.1',
    'author': "Alitec Pte Ltd",
    'depends': [
        'sale', 'stock', 'sale_stock', 'base_automation'
    ],
    'data': ['data/crm.team.csv',
             'views/product.xml',
             'views/sale.xml',
             'views/blanket_sale.xml',
             'views/stock.xml',
             'views/invoice.xml',
             'views/menu.xml',
             'data/automation.xml',
             'security/ir.model.access.csv'
    ],
}