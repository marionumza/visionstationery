# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    urgency = fields.Selection([('normal', 'Normal'),
                                ('urgent', 'Urgent'),
                                ('very_urgent', 'Very Urgent')], string='Urgency', default='normal')

    portal_requester = fields.Char('Portal Requester')
    portal_requester_info = fields.Char('Portal Requester info')
