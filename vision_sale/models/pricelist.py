# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    pricelist_type = fields.Selection([('public', 'Public'),
                                       ('tender', 'Tender')], string='Type', default='public')
