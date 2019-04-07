# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    selected_theme = fields.Many2one('ir.web.theme', string='Selected Theme')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        selected_theme = params.get_param('uppercrust_backend_theme.selected_theme', default=False)
        res.update(selected_theme=selected_theme)
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("uppercrust_backend_theme.selected_theme", self.selected_theme.id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
