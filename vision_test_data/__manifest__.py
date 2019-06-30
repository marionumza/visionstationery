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

    'name': "Vision Test Data",
    'summary': """Test for Vision Stationery""",
    'version': '11.0.1',
    'category': 'Vision',
    'author': "Alitec Pte Ltd",
    'depends': [
        'sale', 'stock'
    ],
    'data': ['data/product.yml',
             'data/partner.yml'
    ],
}