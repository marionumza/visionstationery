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

    'name': "Vision Pricelist",
    'summary': """Pricelist Rules""",
    'category': 'Vision',
    'version': '11.0.03',
        'description': """
Customised Pricelist for Vision Stationery
===========================================
    - last update: 09-Jun-2019
    
        
    """,

    'author': "Alitec Pte Ltd",
    'depends': ['sale', 'vision_sale'
    ],
    'data': ['views/sale.xml',
             'views/pricelist.xml',
             'wizard/assign_pricelist_partner.xml',
             'wizard/remove_pricelist_partner.xml'
    ],
}