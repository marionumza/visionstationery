# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    urgency = fields.Selection([('normal', 'Normal'),
                                ('urgent', 'Urgent'),
                                ('very_urgent', 'Very Urgent')], string='Urgency', default='normal')

    portal_requester = fields.Char('Portal Requester')
    portal_requester_info = fields.Char('Portal Requester info')
    
    
    
#     @api.multi
#     def button_validate(self):
    @api.multi
    def action_done(self):
        self.ensure_one()
        if self.picking_type_id.code == 'outgoing':
            for move in self.move_lines:
                if (move.product_uom_qty < move.quantity_done) and (move.state not in ('done', 'cancel')):
                    raise UserError(_('You cannot validate a transfer if you have done quantity Greater than Initial Demanded.'))
        return super(StockPicking, self).action_done()
    
