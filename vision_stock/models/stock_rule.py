# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    stock_request_rule = fields.Boolean('Request Rule', help='can be automatically assigned to stock request')
