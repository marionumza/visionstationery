# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    min_price = fields.Monetary('Min Sell Price')
    max_price = fields.Monetary('Max Sell Price')
    reserved_qty = fields.Float('Reserved', compute='_compute_reserved_qty')

    @api.onchange('list_price')
    def update_max_price(self):
        self.ensure_one()
        self.max_price = max(self.max_price, self.list_price)

    @api.multi
    def _compute_reserved_qty(self):
        for template in self:
            variant_lst = template.product_variant_ids.mapped('reserved_qty')
            qty = len(variant_lst) > 0 and sum(variant_lst) or 0.0
            template.reserved_qty = qty

    @api.constrains("default_code")
    def _constraint_uniq_default_code(self):
        for record in self:
            other_product_ids =[]
            if record.default_code:
                other_product_ids = self.search([('default_code','=',record.default_code),('id','!=',record.id)])
            if other_product_ids:
                raise ValidationError(_(
                    "Internal Reference must be Unique !"
                ))



class ProductProduct(models.Model):
    _inherit = 'product.product'

    reserved_qty = fields.Float('Reserved', compute='_compute_reserved_qty')

    @api.multi
    def _compute_reserved_qty(self):
        order_id = self.env['sale.order'].search([('unreserved', '=', False)])
        line_id = order_id.mapped('order_line')

        data = {}
        for i in line_id:
            prod = i.product_id.id
            if i.product_id.id in data:
                data[prod] += i.product_uom._compute_quantity(i.product_uom_qty, i.product_id.uom_id)
            else:
                data[prod] = i.product_uom._compute_quantity(i.product_uom_qty, i.product_id.uom_id)

        for product in self:
            product.reserved_qty = product.id in data and data[product.id] or 0.0
        return

 