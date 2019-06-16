# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    origin = fields.Char('Source Document')
    origin_picking_ids = fields.Many2many('stock.picking', 'origin_picking_request', 'request_id', 'picking_id', string='Source Picking')
    origin_count = fields.Integer('Origin Count', compute='_compute_origin_count')

    @api.multi
    def _compute_origin_count(self):
        for rec in self:
            rec.origin_count = len(rec.origin_picking_ids)

    @api.multi
    def action_view_origin(self):
        self.ensure_one()
        action = {'name': 'Stock Picking',
                  'type': 'ir.actions.act_window',
                  'views': [[False, 'tree'], [False, 'form']],
                  'target': 'current',
                  'res_model': 'stock.picking'}
        if len(self.origin_picking_ids) > 1:
            action['domain'] = "[('id', 'in', %s)]" % self.origin_picking_ids.ids
        elif len(self.origin_picking_ids) == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.origin_picking_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.model
    def create_from_stock_move(self, stock_move_ids=None):
        """
        Create a stock request order from stock moves
        aggregate the products, by products uom
        - All the stock moves must have the same source location
        - The source location must be the stock location of a warehouse

        :param stock_move_ids:
        :return: request_order.id
        """

        if not stock_move_ids:
            return
        picking_name = stock_move_ids.mapped('picking_id.name')
        picking_name = len(picking_name)>0 and ", ".join(picking_name)

        location_id, warehouse_id = self._get_location_warehouse(stock_move_ids=stock_move_ids)
        expected_date = fields.Datetime.now()
        values = self._prepare_line_values(stock_move_ids=stock_move_ids, expected_date=expected_date,
                                           location_id=location_id, warehouse_id=warehouse_id)

        values = self._add_route(vals=values, warehouse_id=warehouse_id)

        order_vals = {'warehouse_id': warehouse_id.id,
                      'picking_policy': 'direct',
                      'expected_date': expected_date,
                      'stock_request_ids': values,
                      'origin': picking_name            # Note: the link between picking and request is done in the stock.picking module
                      }
        order_id = self.env['stock.request.order'].create(order_vals)

        return order_id.id

    @api.model
    def _get_location_warehouse(self, stock_move_ids):
        """
        Return the source location, and the warehouse for a list of stock moves, which should all have the same source
        location
        :param stock_move_ids: object
        :return: location_id, warehouse_id
        """
        location_id = stock_move_ids.mapped('location_id')
        if len(location_id) != 1:
            raise ValidationError('Error: the selected stock moves are not supplied from the same source location')

        location_id = location_id[0]
        warehouse_id = self.env['stock.warehouse'].search([('lot_stock_id', '=', location_id.id)])
        if len(warehouse_id) != 1:
            raise ValidationError('The stock moves should originate from the stock location of a warehouse')
        warehouse_id = warehouse_id[0]
        return location_id, warehouse_id

    @api.model
    def _prepare_line_values(self, stock_move_ids=None, expected_date=None, location_id=None, warehouse_id=None):
        if not stock_move_ids or not expected_date or not location_id or not warehouse_id:
            raise ValidationError('Error when preparing the line values for stock request order')

        lst_product = {}
        for m_id in stock_move_ids:
            product = m_id.product_id.id
            if product not in lst_product:
                lst_product[product] = [m_id.product_uom_qty, m_id.product_uom.id]
            else:
                lst_product[product][0] += m_id.product_uom_qty
        values = []

        for product, lst in lst_product.items():
            tpl = (0, 0, {'expected_date': expected_date,
                          'product_id': product,
                          'location_id': location_id.id,
                          'warehouse_id_id': warehouse_id.id,
                          'product_uom_id': lst[1],
                          'product_uom_qty': lst[0]})
            values.append(tpl)
        return values

    @api.model
    def _add_route(self, vals=None, warehouse_id=None):
        if not vals or not warehouse_id:
            return

        route_ids = self.env['stock.location.route'].search([('warehouse_selectable', '=', True),
                                                             ('warehouse_ids', 'in', [warehouse_id.id]),
                                                             ('stock_request_rule', '=', True)])
        route_ids = len(route_ids) > 0 and route_ids.sorted(key=lambda r: r.sequence) or False
        search_loc = {}
        for rec in route_ids:
            pull_id = rec.pull_ids.filtered(lambda l: l.action == 'move' and l.procure_method == 'make_to_stock')
            if len(pull_id) != 1:
                raise ValidationError('the routes of warehouse %s are badly configured' % warehouse_id.name)
            search_loc[pull_id.location_src_id.id] = rec.id

        for item in vals:
            product = item[2]['product_id']
            qty = item[2]['product_uom_qty']
            item[2]['route_id'] = False
            product_id = self.env['product.product'].browse(product)

            for loc, rte in search_loc.items():
                loc_qty = product_id.get_quantity_location(location=loc)
                if loc_qty >= qty:
                    item[2]['route_id'] = rte
                    break

        vals = [(0, 0, item[2]) for item in vals if item[2]['route_id']]
        return vals

    @api.multi
    def unlink(self):
        self.stock_request_ids.unlink()
        return super().unlink()
