# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    pricelist_type = fields.Selection([('public', 'Public'),
                                       ('tender', 'Tender')], string='Type', default='public')


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    uom_id = fields.Many2one('product.uom', 'Unit of Measure')

    @api.onchange('applied_on')
    def onchange_update_uom(self):
        self.ensure_one()
        if self.applied_on in ['3_global', '2_product_category']:
            self.uom_id = False
