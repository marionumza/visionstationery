# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    portal_requester = fields.Char('Portal Requester')
    portal_requester_info = fields.Char('Portal Requester info')
    grouped_line_ids = fields.One2many('account.invoice.grouped.line', 'invoice_id', 'Grouped lines')
    total_grouped_line = fields.Float('Total Grouped Line')
    order_customer_category = fields.Char('Customer Category for Order')
    
    @api.multi
    def action_group_line(self):
        self.ensure_one()
        to_do = self._cost_center_line()
        for cost_center, line_list in to_do.items():
            line_ids = self.env['account.invoice.line'].browse(line_list)
            amount = sum(line_ids.mapped('price_subtotal'))
            vals = {'invoice_id': self.id,
                    'quantity': 1,
                    'price_unit': amount,
                    'price_total': amount,
                    'summary_by': cost_center,
                    'name': 'Consolidated amount'}
            self.env['account.invoice.grouped.line'].create(vals)
        total = len(self.grouped_line_ids) > 0 and sum(self.grouped_line_ids.mapped('price_total')) or 0.0
        self.write({'total_grouped_line': total})

    def _cost_center_line(self):
        """
        Loop through the invoice line
        :return: {cost_center: [id of invoice line]}
        """
        self.ensure_one()
        res = {}
        for rec in self.invoice_line_ids:
            cost_center = rec.get_cost_center()
            if cost_center in res:
                res[cost_center].append(rec.id)
            else:
                res[cost_center] = [rec.id]
        return res

    @api.multi
    def action_group_line_reset(self):
        self.ensure_one()
        self.grouped_line_ids.unlink()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', compute='_get_sale_order')

    @api.multi
    def _get_sale_order(self):
        for rec in self:
            order_ids = rec.sale_line_ids.mapped('order_id')
            order_id = len(order_ids) > 0 and order_ids[0] or False
            rec.sale_order_id = order_id

    def get_cost_center(self):
        self.ensure_one()
        order_ids = self.sale_line_ids and self.sale_line_ids.mapped('order_id') or False

        if not order_ids:
            return False

        if len(order_ids) > 1:
            message = 'One invoice line (%s) is linked to two different orders, it is not possible to get the cost center' % self.name
            raise ValidationError(message)

        return order_ids[0].cost_center


class AccountInvoiceGroupLine(models.Model):
    _name = 'account.invoice.grouped.line'
    _description = 'Grouped Invoice Lines'

    invoice_id = fields.Many2one('account.invoice', 'Invoice', copy=False, ondelete='cascade')
    name = fields.Text('Description')
    quantity = fields.Float('Quantity')
    price_unit = fields.Float('Price Unit')
    price_total = fields.Float('Amount')
    summary_by = fields.Char('Summary by')
