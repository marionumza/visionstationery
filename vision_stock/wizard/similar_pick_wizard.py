# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class SimilarPickWizard(models.TransientModel):
    _name = 'similar.pick.wizard'

    picking_id = fields.Many2one('stock.picking', 'Delivery order')
    delivery_date = fields.Date('Delivery date')
    line_ids = fields.One2many('similar.pick.line', 'similar_id', string='Line')
    number_similar_pick = fields.Integer('Number of Similar Orders')

    @api.model
    def default_get(self, fields_list):
        res = models.TransientModel.default_get(self, fields_list)
        active_ids = self._context.get('active_ids', False)
        if not active_ids:
            return

        get_param = self.env['ir.config_parameter'].sudo().get_param
        nb_similar_line = int(get_param('default_nb_similar_line') or '0')

        pick_id = self.env['stock.picking'].browse(active_ids[0])
        vals = self.get_similar_vals(pick_id.id)
        res.update({'picking_id': pick_id.id,
                    'number_similar_pick': nb_similar_line,
                    'delivery_date': pick_id.scheduled_date[:10],
                    'line_ids': vals})
        return res

    @api.model
    def get_similar_vals(self, pick):
        """
        prepare the values for the creation of the lines for the wizard
        :param pick:
        :return:
        """
        pick_id = self.env['stock.picking'].browse(pick)
        pick_list = pick_id.compute_list_similar()
        vals = [(0, 0, {'pick_id': i[0],
                        'nb_line': i[1],
                        'nb_similar_line': i[2],
                        'similarity_rate': i[3]}) for i in pick_list]
        return vals

    @api.multi
    def action_get_similar(self):
        """
        triggered by a button, to refresh the list of similar picking
        :return:
        """
        vals = self.get_similar_vals(self.picking_id.id)
        self.update({'line_ids': vals})
        action = {'name': 'Request Stock with Auto Selection',
                  'type': "ir.actions.act_window",
                  'views': [[False, 'form']],
                  'target': 'new',
                  'res_model': 'similar.pick.wizard',
                  'res_id': self.id
                  }

        return action

    @api.multi
    def action_request(self):
        pick_ids = self.line_ids.mapped('pick_id')
        request_order = pick_ids.create_request_order()
        action = {'name': 'Stock Request Order',
                  'type': "ir.actions.act_window",
                  'views': [[False, 'form']],
                  'target': 'current', 'res_model': 'stock.request.order',
                  'res_id': request_order}
        return action


class SimilarPickLine(models.TransientModel):
    _name = 'similar.pick.line'
    _order = 'similarity_rate desc, id'

    similar_id = fields.Many2one('similar.pick.wizard', string='Similar Wizard')
    pick_id = fields.Many2one('stock.picking', 'Picking')
    nb_line = fields.Integer('# lines')
    nb_similar_line = fields.Integer('# common products')
    similarity_rate = fields.Float('Similarity rate')
