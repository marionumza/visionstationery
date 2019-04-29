# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    min_price = fields.Monetary('Min Sell Price')
    max_price = fields.Monetary('Max Sell Price')
