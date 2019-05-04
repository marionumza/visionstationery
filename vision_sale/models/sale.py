# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('Draft'))

    quotation_no = fields.Char('Quotation No')
    blanket = fields.Boolean('Blanket Contract', default=False)

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('approved', 'Approved'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    def _assign_name(self):
        self.ensure_one()
        if self.name == _('Draft'):
            if self.company_id:
                return self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(
                    'sale.order') or _('Draft')
            else:
                return self.env['ir.sequence'].next_by_code('sale.order') or _('Draft')
        else:
            return self.name

    @api.multi
    def action_confirm(self):
        res = True
        for rec in self:
            vals = {}
            if rec.blanket:
                vals = {'state': 'done'}
            else:
                if rec.state != 'approved':
                    raise ValidationError(_('Order %s is not approved') % rec.name)
                res = super(SaleOrder, self).action_confirm()

            vals['name'] = rec._assign_name()
            rec.write(vals)
        return res

    @api.multi
    def action_new_related_order(self):
        self.ensure_one()
        new_order_id = self.copy()
        new_order_id.write({'origin': self.name,
                            'state': 'approved',
                            'blanket': False})

        imd = self.env['ir.model.data']
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        action = {
                'name': 'Sale Order',
                'type': "ir.actions.act_window",
                'views': [[form_view_id, 'form']],
                'target': 'current',
                'res_model': 'sale.order',
                'res_id': new_order_id.id
                }
        return action

    @api.multi
    def action_view_related_order(self):
        self.ensure_one()
        self.ensure_one()
        order_id = self.env['sale.order'].search([('origin', '=', self.name)])
        imd = self.env['ir.model.data']

        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')

        result = {
            'name': 'Sale Order',
            'type': "ir.actions.act_window",
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': 'current',
            'res_model': 'sale.order',
        }
        if len(order_id) > 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        elif len(order_id) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = order_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.multi
    def action_approve(self):
        imd = self.env['ir.model.data']
        web_team = imd.xmlid_to_res_id('vision_sale.vision_web_team')
        blanket_team = imd.xmlid_to_res_id('vision_sale.vision_blanket_team')
        special_team_domain = [web_team, blanket_team]

        for rec in self:

            if rec.team_id and rec.team_id.id in special_team_domain:
                rec.write({'state': 'approved'})
                rec.action_confirm()
                continue
            if not self.env.user.has_group('base.group_system'):
                raise ValidationError('You are not authorised to approve quotations')

            vals = {'state': 'approved'}
            vals['name'] = rec._assign_name()
            rec.write(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('approved', 'Approved'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], related='order_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')

    price_unit = fields.Float('Unit Price', readonly=True, states={'draft': [('readonly', False)]})
    blanket_delivered_qty = fields.Float('Bkt Delivered Qty', compute='_compute_blanket_qty')

    def _compute_blanket_qty(self):
        for rec in self:
            rec.blanket_delivered_qty = 0.0

    @api.constrains('price_unit')
    def check_status_before_update_price(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('You cannot modify the price for an approved order. Set it to draft first'))

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        sale_channel = self.order_id.team_id and self.order_id.team_id.id or False
        blanket_channel = self.env.ref('vision_sale.vision_blanket_team') and self.env.ref(
            'vision_sale.vision_blanket_team').id or False

        if not sale_channel or (sale_channel != blanket_channel):
            return super(SaleOrderLine, self).product_uom_change()

    def _onchange_product_id_check_availability(self):
        return {}
