# -*- coding: utf-8 -*-

from odoo import api, fields, models, _



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    comment = fields.Char('Comment')



    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        res = super(PurchaseOrderLine, self)._onchange_quantity()
        if not self.product_id:
            return
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom)
        if seller:
             self.comment = seller.comment



