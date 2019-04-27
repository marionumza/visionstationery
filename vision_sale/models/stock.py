# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    def create_resupply_move(self):
        """
        :param self: singleton
        :param expected_date: char

        Check all the unfullfilled reservation (filter by expected date) from the stock location of the warehouse
        For each product, aggregate the required qty, and create a stock request for the warehouse and location
        :return: picking_ids
        """

        self.ensure_one()
        location_id = self.lot_stock_id
        domain = [('state', '=', 'confirmed'), ('location_id', '=', location_id.id)]   # TODO: filter by date
        stock_move_ids = self.env['stock.move'].search(domain)
        need = {}           # { product_id.id: {uom_id.id:  qty, uom_id2.id: qty2}} }

        for move_id in stock_move_ids:
            product = move_id.product_id.id
            uom = move_id.product_uom.id
            qty = move_id.product_uom_qty
            if product in need and uom in need[product]:
                need[product][uom] += qty
            elif product in need:
                need[product][uom] = qty
            else:
                need[product] = {uom: qty}

        res = []
        for p in need:
            for uom in need[p]:
                vals = {'product_id': p,
                        'location_id': location_id.id,
                        'warehouse_id_id': self.id,
                        'product_uom_id': uom,
                        'product_uom_qty': need[p][uom]}
                request_id = self.env['stock.request'].create(vals)
                request_id.action_confirm()
                res.append(request_id.id)
        return res
