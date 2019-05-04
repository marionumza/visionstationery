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

        request_order = self.env['stock.request.order'].create_from_stock_move(stock_move_ids=stock_move_ids)
        return request_order

    def get_wh_and_route(self):
        """
        for a single warehouse, it will search for the "Normal" and "Automated" Warehouse, as well as the supply routes
        from these warehouses
        :return: ids of normal_wh, automated_wh, normal_route, automated_route
        """
        self.ensure_one()
        automated_wh_id = self.env['stock.warehouse'].search([('name', 'like', 'Automated')])
        normal_wh_id = self.env['stock.warehouse'].search([('name', 'like', 'Normal')])
        if len(automated_wh_id) != 1 or len(normal_wh_id) != 1:
            raise ValidationError('Configuration Error on names of warehouses')

        automated_wh_id = automated_wh_id[0]
        normal_wh_id = normal_wh_id[0]

        normal_route_id = self.env['stock.location.route'].search([('warehouse_selectable', '=', True),
                                                                   ('warehouse_ids', 'in', [self.id]),
                                                                   ('name', 'like', 'Normal')])
        automated_route_id = self.env['stock.location.route'].search([('warehouse_selectable', '=', True),
                                                                      ('warehouse_ids', 'in', [self.id]),
                                                                      ('name', 'like', 'Automated')])
        if len(normal_route_id) != 1 or len(automated_route_id) != 1:
            raise ValidationError('Configuration Error on names of routes')
        return normal_wh_id.id, automated_wh_id.id, normal_route_id.id, automated_route_id.id


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def create_request_order(self):
        move_ids = self.mapped('move_lines')
        request_order = self.env['stock.request.order'].create_from_stock_move(stock_move_ids=move_ids)
        return request_order
