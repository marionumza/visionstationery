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

    'name': "Vision Purchase",
    'summary': """Customised Purchase for Vision Stationery""",
    'category': 'Vision',
    'version': '11.0.1.0',
    'author': "Alitec Pte Ltd",
    'description': """ 
                - Last Update: 08-JAN-2020
                    """,
    'depends': [
        'sale', 'stock', 'sale_stock', 'base_automation'
    ],
    'data': [
             'security/ir.model.access.csv',
             'views/product.xml',
             'views/purchase.xml',
             
    ],
}