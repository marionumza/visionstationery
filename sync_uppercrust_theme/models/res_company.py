# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import odoo
from odoo import models, fields, api, _

class res_company(models.Model):
    _inherit = "res.company"

    @api.one
    @api.depends('partner_id', 'partner_id.image')
    def _get_default_logo_web(self):
        self.web_company_logo = self.partner_id.image
    
    web_company_logo = fields.Binary(compute='_get_default_logo_web', string="Logo Web", store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
