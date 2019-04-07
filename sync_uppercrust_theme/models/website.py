# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import odoo
from odoo import models, fields, api, _

class res_partner(models.Model):
    _inherit = "res.partner"

    def google_map_address(self, zoom=8):        
        params = {
            'q': '%s, %s %s, %s' % (self.street or '', self.city  or '', self.zip or '', self.country_id and self.country_id.name_get()[0][1] or ''),
        }
        return params['q'].replace(',', ' ')

class res_company(models.Model):
    _inherit = "res.company"

    @api.multi
    def google_map_address(self, zoom=8):
        partner = self.sudo().partner_id
        return partner and partner.google_map_address(zoom) or None

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
