# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging

from odoo import api, fields, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)

State = [
    ('draft', 'Draft'),
    ('done', 'Done'),
    ('cancel', 'Cancel')
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    wk_website_loyalty_points = fields.Float(
        string='Website Loyalty Points',
        help='The points are the points with which the user is awarded of being Loyal !',
        digits=dp.get_precision('Loyalty Points')
    )


class res_users(models.Model):
    _inherit = 'res.users'

    wk_website_loyalty_points = fields.Float(
        related='partner_id.wk_website_loyalty_points'
    )

    @api.model
    def create(self, vals):
        ir_model_data = self.env['ir.model.data']
        portal_user_id = ir_model_data.get_object_reference(
            'base', 'group_portal')[1]
        wk_loyalty_program_id = self.env['ir.default'].sudo().get('res.config.settings', 'wk_loyalty_program_id')
        groups_id = vals.get('groups_id')
        portal_signup = (self.env.ref('base.group_portal').id in groups_id[0][2]) if groups_id else False
        if wk_loyalty_program_id  and (portal_signup or vals.get('in_group_1')):
            loyalty_obj = self.env['website.loyalty.management'].browse(wk_loyalty_program_id)
            wk_website_loyalty_points = loyalty_obj._fetch_signup_loyalty_points()
            if wk_website_loyalty_points:
                vals['wk_website_loyalty_points'] = wk_website_loyalty_points
                res = super(res_users, self).create(vals)
                res.partner_id.wk_website_loyalty_points =wk_website_loyalty_points
                history_vals = {
                    'partner_id': res.partner_id.id,
                    'loyalty_id': loyalty_obj.id,
                    'points_processed': wk_website_loyalty_points,
                    'loyalty_process': 'addition',
                    'process_reference': 'Sign Up',
                }

                self.env['website.loyalty.history'].sudo().create(history_vals)
                return res
        return super(res_users, self).create(vals)




class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total')
    def _compute_wk_website_loyalty_points(self):
        for order in self:
            if order.wk_loyalty_state not in ['cancel', 'done']:
                amount = order.amount_total
                obj = order.wk_loyalty_program_id# or self.env['website.loyalty.management'].get_active_obj()
                if obj:
                    wk_website_loyalty_points = order.wk_extra_loyalty_points + obj.get_loyalty_points(amount)
                    order.update({
                    'wk_website_loyalty_points': wk_website_loyalty_points,
                    })
    @api.model
    def _get_default_wk_loyalty_program_id(self):
        return self.env['ir.default'].sudo().get('res.config.settings', 'wk_loyalty_program_id')


    wk_extra_loyalty_points = fields.Float(
        string='Extra Loyalty Points',
        copy=False
    )
    wk_loyalty_program_id = fields.Many2one(
        string = 'Loyalty Program',
        comodel_name = 'website.loyalty.management',
        default = _get_default_wk_loyalty_program_id
    )
    wk_website_loyalty_points = fields.Float(
        string='Loyalty Points',
        store=True,
        readonly=True,
        compute='_compute_wk_website_loyalty_points',
        track_visibility='always'
    )
    wk_loyalty_state = fields.Selection(
        selection=State,
        string='Loyalty Stage',
        default='draft',
        copy=False
    )

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for record in self.filtered('wk_loyalty_program_id'):
            loyalty_obj = record.wk_loyalty_program_id
            loyalty_obj.update_partner_loyalty(record,'confirm')
        return res

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for record in self.filtered('wk_loyalty_program_id'):
            loyalty_obj = record.wk_loyalty_program_id
            loyalty_obj.cancel_redeem_history(record)
        return res
