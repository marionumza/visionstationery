# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class Bom(models.Model):
    _inherit = 'mrp.bom'

    type = fields.Selection([('normal', 'Manufacture/Assemble this product'),
                             ('phantom', 'kit')])
