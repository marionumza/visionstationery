from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class SmartStockRequest(models.TransientModel):
    _name = 'smart.stock.request'

    @api.multi
    def action_confirm(self):
        domain = [('picking_type_id.auto_stock_request', '=', True), ('state', 'in', ('confirmed', 'waiting'))]
        pick_ids = self.env['stock.picking'].search(domain)
        if len(pick_ids) == 0:
            return True
        pick_ids = pick_ids.sorted(key=lambda r: len(r.move_lines))
        selected_id = pick_ids[len(pick_ids)-1]

        get_param = self.env['ir.config_parameter'].sudo().get_param
        nb_similar_pick = int(get_param('default_nb_similar_line') or '0')
        similar_pick_list = selected_id.compute_list_similar(nb=nb_similar_pick)
        similar_pick = [p['pick_id'] for p in similar_pick_list if p['selected']]
        similar_pick.append(selected_id.id)
        similar_pick_ids = self.env['stock.picking'].browse(similar_pick)

        request_order = similar_pick_ids.create_request_order()
        action = {'name': 'Stock Request Order',
                  'type': "ir.actions.act_window",
                  'views': [[False, 'form']],
                  'target': 'current', 'res_model': 'stock.request.order',
                  'res_id': request_order}
        return action


