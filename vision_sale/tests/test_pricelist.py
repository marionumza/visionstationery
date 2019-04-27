# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class SelectProductSO(TransactionCase):

    def setUp(self):
        super(SelectProductSO, self).setUp()
        user = self.env.ref('base.user_root')

        unit_id = self.env.ref('product.product_uom_unit')
        dozen_id = self.env.ref('product.product_uom_dozen')
        vals = {'name': 'test_product',
                'uom_id': unit_id.id,
                }
        self.product_id = self.env['product.product'].sudo(user).create(vals)

        partner_vals = {'name': 'test_customer'}
        self.partner_id = self.env['res.partner'].sudo(user).create(partner_vals)

        pricelist_vals = {'name': 'test_pricelist',
                          'pricelist_type': 'public',
                          'item_ids': [(0, 0, {'applied_on': '0_product_variant',
                                               'compute_price': 'fixed',
                                               'product_id': self.product_id.id,
                                               'uom_id': unit_id.id,
                                               'fixed_price': 1.0}),
                                       (0, 0, {'applied_on': '0_product_variant',
                                               'compute_price': 'fixed',
                                               'product_id': self.product_id.id,
                                               'uom_id': dozen_id.id,
                                               'fixed_price': 12.0})
                                       ]}
        # print(pricelist_vals)
        self.pricelist_id = self.env['product.pricelist'].sudo(user).create(pricelist_vals)

    def test_create_so_success_1(self):
        """
        create a SO, select the customer and the pricelist
        Add a line, select the product, the uom, the price should be taken from the pricelist accordingly
        :return:
        """
        user = self.env.ref('base.user_root')
        unit_id = self.env.ref('product.product_uom_unit')
        dozen_id = self.env.ref('product.product_uom_dozen')

        so_vals = {'partner_id': self.partner_id.id,
                   'pricelist_id': self.pricelist_id.id}
        so_id = self.env['sale.order'].sudo(user).create(so_vals)

        line_vals = {'order_id': so_id.id,
                     'product_id': self.product_id.id,
                     'product_uom': dozen_id.id,
                     'product_uom_qty': 1.0}

        print('2A: ', line_vals)

        sale_order_line = self.env['sale.order.line']
        specs = sale_order_line._onchange_spec()
        updates = sale_order_line.onchange(line_vals, ['product_uom'], specs)
        value = updates.get('value', {})
        for name, val in value.items():
            if isinstance(val, tuple):
                value[name] = val[0]
        line_vals.update(value)

        print('2B: ', line_vals)

        line_id = sale_order_line.create(line_vals)
        self.assertEqual(line_id.price_unit, 12.0)

    def test_create_so_success_2(self):
        """
        create a SO, select the customer and the pricelist
        Add a line, select the product, the uom, the price should be taken from the pricelist accordingly
        :return:
        """
        user = self.env.ref('base.user_root')
        unit_id = self.env.ref('product.product_uom_unit')
        dozen_id = self.env.ref('product.product_uom_dozen')

        so_vals = {'partner_id': self.partner_id.id,
                   'pricelist_id': self.pricelist_id.id}
        so_id = self.env['sale.order'].sudo(user).create(so_vals)

        line_vals = {'order_id': so_id.id,
                     'product_id': self.product_id.id,
                     'product_uom': unit_id.id,
                     'product_uom_qty': 1.0}

        print('1A: ', line_vals)

        sale_order_line = self.env['sale.order.line']
        specs = sale_order_line._onchange_spec()
        updates = sale_order_line.onchange(line_vals, ['product_uom'], specs)
        value = updates.get('value', {})
        for name, val in value.items():
            if isinstance(val, tuple):
                value[name] = val[0]
        line_vals.update(value)

        print('1B: ', line_vals)

        line_id = sale_order_line.create(line_vals)
        self.assertEqual(line_id.price_unit, 1.0)

    # def test_create_so_fail(self):
    #     """
    #     create a SO, select the customer and the pricelist
    #     Add a line, select the product, the uom, the price should be taken from the pricelist accordingly
    #     :return:
    #     """
    #     user = self.env.ref('base.user_root')
    #     unit_id = self.env.ref('product.product_uom_unit')
    #     dozen_id = self.env.ref('product.product_uom_dozen')
    #
    #     so_vals = {'partner_id': self.partner_id.id,
    #                'pricelist_id': self.pricelist_id.id}
    #     so_id = self.env['sale.order'].sudo(user).create(so_vals)
    #
    #     line_vals = {'order_id': so_id.id,
    #                  'product_id': self.product_id.id,
    #                  'product_uom': dozen_id.id}
    #     sale_order_line = self.env['sale.order.line']
    #     specs = sale_order_line._onchange_spec()
    #     updates = sale_order_line.onchange(line_vals, [], specs)
    #     value = updates.get('value', {})
    #     for name, val in value.items():
    #         if isinstance(val, tuple):
    #             value[name] = val[0]
    #     line_vals.update(value)
    #     line_id = sale_order_line.create(line_vals)
    #     self.assertEqual(line_id.price_unit, 2.0)

