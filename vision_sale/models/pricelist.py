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
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        self.ensure_one()
        domain = {'uom_id':[]}
        if self.product_id:
            domain.update({'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]})
        result = {'domain': domain}
        return result
    
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        self.ensure_one()
        domain = {'uom_id':[]}
        if self.product_tmpl_id:
            domain.update({'uom_id': [('category_id', '=', self.product_tmpl_id.uom_id.category_id.id)]})
        result = {'domain': domain}
        return result

        
        
  