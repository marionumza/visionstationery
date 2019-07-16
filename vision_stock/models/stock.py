# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from operator import itemgetter
import logging
_logger = logging.getLogger(__name__)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    auto_stock_request = fields.Boolean('Auto Stock Request', default=False)


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    _order = 'sequence,name,id'

    sequence = fields.Integer('Priority', default=10)

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

    supply_request_ids = fields.Many2many('stock.request.order', 'origin_picking_request', 'picking_id', 'request_id', string='Supply Request')
    supply_request_count = fields.Integer('Supply request count', compute='_compute_supply_request_data')
    supply_pick_ids = fields.Many2many('stock.picking', string='Supply Picking', compute='_compute_supply_request_data')

    @api.multi
    def create_request_order(self):
        move_ids = self.mapped('move_lines')
        request_order = self.env['stock.request.order'].create_from_stock_move(stock_move_ids=move_ids)
        self.write({'supply_request_ids': [(4, request_order, 0)]})
        return request_order

    @api.multi
    def _compute_supply_request_data(self):
        for rec in self:
            valid_request_ids = rec.supply_request_ids.filtered(lambda r: r.state != 'cancel')
            rec.supply_request_count = len(valid_request_ids)

            # get the list of product in the picking
            searched_product_ids = rec.move_lines.mapped('product_id')

            # get the list of supply pickings related to all the stock requests linked to this picking
            supply_request_ids = rec.supply_request_ids
            supply_picking_ids = supply_request_ids.mapped('picking_ids')

            # Filter - keep only the supply pickings that contains at least one product in the picking.
            # Several stock pickings are linked to a single stock request order
            # one stock request order is linked to several supply pickings

            supply_move_ids = supply_picking_ids.mapped('move_lines')
            selected_move_ids = supply_move_ids.filtered(lambda r: r.product_id in searched_product_ids and r.state != 'cancel')
            supply_picking_ids = selected_move_ids.mapped('picking_id')

            vals = len(supply_picking_ids) > 0 and [(6, 0, [i.id for i in supply_picking_ids])] or False
            rec.supply_pick_ids = vals

    @api.multi
    def show_supply_request(self):
        self.ensure_one()
        requests = self.supply_request_ids.ids

        action = self.env.ref(
            'stock_request.stock_request_order_action').read()[0]

        if len(requests) == 0:
            return
        if len(requests) > 1:
            action['domain'] = [('id', 'in', requests)]
        elif requests:
            action['views'] = [
                (self.env.ref('stock_request.stock_request_order_form').id,
                 'form')]
            action['res_id'] = requests[0]

        return action

    def compute_list_similar(self, nb=None):
        """
        from a singleton, return a list of similar picking
        :param: nb: number of picking that must be selected=True
        :return: list of similar pickings
                [{'pick_id': id,
                  'nb_line': xx,
                  'nb_similar_line': xx,
                  'similarity_rate': xxx,
                  'urgency': xx}]
        """
        self.ensure_one()
        domain = [('state', '=', 'confirmed'), ('picking_type_id', '=', self.picking_type_id.id)]
        pick_ids = self.env['stock.picking'].search(domain)
        pick_ids = pick_ids - self
        product_list = self.move_lines.mapped('product_id')
        res = []
        for p in pick_ids:
            shared_line = [m.id for m in p.move_lines if m.product_id in product_list]
            ct = len(shared_line)
            nb_line = p.move_lines and len(p.move_lines) or 0
            elt = {'pick_id': p.id,
                   'nb_line': nb_line,
                   'nb_similar_line': ct,
                   'similarity_rate': nb_line and ct/nb_line * 100 or 0,
                   'urgency': p.urgency}
            res.append(elt)

        sorted_res = self.compute_priority(res=res)
        sorted_res = self.select_pickings(res=sorted_res, nb=nb)
        return sorted_res

    @api.model
    def compute_priority(self, res=None):
        """
        from a list of dictionary [{'pick_id': xxx, 'nb_line': xxx, 'common_lines': xxx, 'similarity_rate': xxx, 'urgency': xxx}]
        return the same list, but sorted
        :param res:
        :return: sorted res
        """
        if not res:
            return res

        sorted_res = sorted(res, key=itemgetter('pick_id'))
        sorted_res = sorted(sorted_res, key=itemgetter('urgency'), reverse=True)
        sorted_res = sorted(sorted_res, key=itemgetter('similarity_rate'), reverse=True)
        return sorted_res

    @api.model
    def select_pickings(self, res=None, nb=None):
        """
        select the first nb record in the list. If nb is none, get the default qty from the configuration
        :param res: [{'id': xxx, 'nb_line': xxx, 'common_lines': xxx, 'similarity_rate': xxx, 'urgency': xxx}]
        :param nb: number of pickings that needs to be selected=True
        :return: [{'id': xxx, 'nb_line': xxx, 'common_lines': xxx, 'similarity_rate': xxx, 'urgency': xxx, 'selected': Boolean}]
        """
        if not res:
            return res
        if not nb:
            get_param = self.env['ir.config_parameter'].sudo().get_param
            nb = int(get_param('default_nb_similar_line') or '0')

        for r in res:
            r['selected'] = False

        for n in range(min([nb, len(res)])):
            res[n]['selected'] = True

        return res

    @api.model
    def select_reference_pick(self):
        """
        Returns a picking that will be used as a reference for the automatic stock request
        :return:
        """
        auto_pick_ids = self.env['stock.picking.type'].search([('auto_stock_request', '=', True)])
        if len(auto_pick_ids) == 0:
            return
        domain = [('state', '=', 'confirmed'), ('picking_type_id', 'in', auto_pick_ids.ids)]
        pick_ids = self.env['stock.picking'].search(domain)
        selected_pick_id = pick_ids.sorted(key=lambda r: r.name)[0]
        return selected_pick_id

    @api.model
    def cron_generate_stock_request(self):
        """
        Select a reference picking
        Find similar pickings
        Generate a stock request for all of them

        :return:
        """
        reference_pick_id = self.select_reference_pick()
        if not reference_pick_id:
            return

        # Get the list of pickings from which to create a stock request
        similar_lst = reference_pick_id.compute_list_similar()

        get_param = self.env['ir.config_parameter'].sudo().get_param
        nb_similar_line = int(get_param('default_nb_similar_line') or '3')

        similar_lst = len(similar_lst) > nb_similar_line and similar_lst[:nb_similar_line] or similar_lst
        pick_lst = [i[0] for i in similar_lst]
        pick_lst.append(reference_pick_id.id)
        pick_ids = self.env['stock.picking'].browse(pick_lst)

        request_order = pick_ids.create_request_order()
        return request_order

