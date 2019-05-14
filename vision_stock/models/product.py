# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_quantity_location(self, location=None):
        """
        for a singleton, return the quantity on hane in the location
        :param location: integer
        :return: float
        """
        self.ensure_one()
        if not location:
            return 0.0
        ctx = {'location': location}
        domain_quant = self.env['product.product'].with_context(ctx)._get_domain_locations()[0]
        domain_quant.append(('product_id', '=', self.id))
        quant_ids = self.env['stock.quant'].search(domain_quant)
        quantity = quant_ids and sum(quant_ids.mapped('quantity')) or 0.0
        return quantity
