# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class AssignPricelistPartner(models.TransientModel):
    _name = 'assign.pricelist.partner'

    partner_id = fields.Many2one('res.partner', string='Customer', domain="[('customer', '=', True)]")
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    def action_assign(self):
        if not self.partner_id or not self.pricelist_id:
            return
        return self.pricelist_id.assign_partner(self.partner_id)