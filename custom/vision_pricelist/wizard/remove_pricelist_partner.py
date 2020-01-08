# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class RemovePricelistPartner(models.TransientModel):
    _name = 'remove.pricelist.partner'

    line_ids = fields.One2many('remove.pricelist.partner.line', 'wizard_id', string='Partner')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    @api.model
    def default_get(self, fields_list):
        defaults = super(RemovePricelistPartner, self).default_get(fields_list)
        pricelist = self.env.context.get('active_id', False)
        defaults['pricelist_id'] = pricelist
        pricelist_id = pricelist and self.env['product.pricelist'].browse(pricelist) or False
        partner_ids = pricelist_id.partner_ids
        vals = len(partner_ids) > 0 and [(0, 0, {'partner_id': i.id}) for i in partner_ids] or []
        defaults['line_ids'] = vals
        return defaults

    @api.multi
    def action_remove(self):
        if not self.pricelist_id:
            return
        partner_ids = self.line_ids.mapped('partner_id')
        partner_ids.write({'property_product_pricelist': self.pricelist_id.id})


class RemovePricelistPartnerLine(models.TransientModel):
    _name = 'remove.pricelist.partner.line'

    wizard_id = fields.Many2one('remove.pricelits.partner', string='Order')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)