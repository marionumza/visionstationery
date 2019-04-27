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

            if self.name == _('Draft'):
                if rec.company_id:
                    vals['name'] = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code('sale.order') or _('Draft')
                else:
                    vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('Draft')
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
            rec.write({'state': 'approved'})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        pricelist_item_obj = self.env['product.pricelist.item']
        if self.order_id.pricelist_id.pricelist_type == 'tender':
            pricelist_item_ids = pricelist_item_obj.search([('pricelist_id','=',self.order_id.pricelist_id.id),
                                        ('product_id','=',self.product_id.id)])
            if not pricelist_item_ids:
                pricelist_item_ids = pricelist_item_obj.search([('pricelist_id','=',self.order_id.pricelist_id.id),
                                        ('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
            
            for pricelist_item in pricelist_item_ids:
                if pricelist_item.uom_id:
                     self.update({'product_uom': pricelist_item.uom_id.id})
                     result.get('domain', {}).update({'product_uom': [('id', '=', pricelist_item.uom_id.id)]})
        return result

    def _get_domain(self):
        """
        for a singleton, get the list of allowable uom for the selected product
        the list of allowable uom is taken from the pricelist
        :return: list of id for uom [ , , ]
        """
        self.ensure_one()
        domain = []
        return domain

