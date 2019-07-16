# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from collections import defaultdict
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons import decimal_precision as dp



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pricelist_id = fields.Many2one('product.pricelist', states={'new': [('readonly', False)],
                                                                'draft': [('readonly', False)],
                                                                'sent': [('readonly', False)]})

    partner_id = fields.Many2one('res.partner', states={'draft': [('readonly', False)],
                                                        'sent': [('readonly', False)],
                                                        'new': [('readonly', False)]})

    picking_policy = fields.Selection(states={'new': [('readonly', False)],
                                              'draft': [('readonly', False)],
                                              'sent': [('readonly', False)]})

    warehouse_id = fields.Many2one('stock.warehouse', states={'new': [('readonly', False)],
                                                              'draft': [('readonly', False)],
                                                              'sent': [('readonly', False)]})

    quotation_no = fields.Char('Quotation No')
    blanket = fields.Boolean('Blanket Contract', default=False)
    urgency = fields.Selection([('normal', 'Normal'),
                                ('urgent', 'Urgent'),
                                ('very_urgent', 'Very Urgent')], string='Urgency', default='normal', readonly=True,
                               states={'new': [('readonly', False)], 'draft': [('readonly', False)]})
    unreserved = fields.Boolean('Unreserved', default=True)

    order_customer_category = fields.Char('Customer Category for Order')
    department = fields.Char('Department')
    cost_center = fields.Char('Cost Center')
    portal_requester = fields.Char('Portal Requester')
    portal_requester_info = fields.Char('Portal Requester info')
    portal_requester_id = fields.Char('Portal Requester ID')
    team_name = fields.Char(related='team_id.name', string='Channel name', readonly=True)

    state = fields.Selection([
        ('new', 'New'),
        ('draft', 'Quotation'),
        ('approved', 'Approved'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='new')

    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            vals['name'] = 'New Quote'
        return super(SaleOrder, self).create(vals)

    def _assign_name(self):
        self.ensure_one()
        if self.name == _('New Quote'):
            if self.company_id:
                return self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(
                    'sale.order') or _('Draft')
            else:
                return self.env['ir.sequence'].next_by_code('sale.order') or _('Draft')
        else:
            return self.name

    @api.multi
    def toggle_reservation(self):
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise ValidationError('You are not authorised to change the reservation')
        self.unreserved = not self.unreserved

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
            vals['unreserved'] = True
            rec.write(vals)
        return res

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        self.write({'unreserved': True})
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
    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent'])
        return orders.write({
            'state': 'new',
        })

    @api.multi
    def action_quotation(self):
        orders = self.filtered(lambda s: s.state == 'new')
        line_ids = orders.mapped('order_line')
        ok = all(line_ids.mapped('line_ok'))
        if not ok:
            raise ValidationError('Pricing Error - please verify the unchecked lines')

        for l in line_ids:
            l.write({'price_unit': l.proposed_price_unit})

        return orders.write({'state': 'draft'})

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

    @api.multi
    def unlink(self):
        order_to_change = self.filtered(lambda r: r.state == 'new')
        order_to_change.write({'state': 'cancel'})
        return super(SaleOrder, self).unlink()

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['order_customer_category'] = self.order_customer_category
        return res
    
    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}

        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id, order.order_customer_category)
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.origin]
                    invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                        invoices_name[group_key].append(order.client_order_ref)

                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order

        for group_key in invoices:
            invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
                                       'origin': ', '.join(invoices_origin[group_key])})

        if not invoices:
            raise UserError(_('There is no invoiceable line.'))

        for invoice in invoices.values():
            invoice.compute_taxes()
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoiceable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_total < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    state = fields.Selection([
        ('new', 'New'),
        ('draft', 'Quotation'),
        ('approved', 'Approved'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], related='order_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')

    price_unit = fields.Float('Unit Price', readonly=True,
                              states={'draft': [('readonly', False)], 'new': [('readonly', False)]})
    blanket_delivered_qty = fields.Float('Bkt Delivered Qty', compute='_compute_blanket_qty')
    line_ok = fields.Boolean('Checked', compute='_check_line', store=True)
    proposed_price_unit = fields.Float('Proposed Price', help='Proposed price')
    final_price = fields.Float('RSP', compute='_check_line', help='Recommended Sell Price')

    # The only purpose of the "final_price" is to allow the user to see the price_unit, without the possibility
    # to modify it directly.
    # - If price_unit is a readonly field, it is not possible to modify it, even from backend
    # - the user enter a proposed_price, if the proposed price is accepted, then the proposed price becomes the
    #   price_unit

    @api.depends('price_unit')
    def _check_line(self):
        for rec in self:
            rec.line_ok = rec._check_price_within_allowed_range()
            rec.final_price = rec.price_unit
        return

    @api.onchange('price_unit')
    def update_proposed_price(self):
        for rec in self:
            rec.proposed_price_unit = rec.price_unit

    # @api.constrains('price_unit')
    def _check_price_within_allowed_range(self):
        for rec in self:
            if not rec.product_id:
                continue
            min_price = rec.product_id.uom_id._compute_price(rec.product_id.min_price, rec.product_uom)
            max_price = rec.product_id.uom_id._compute_price(rec.product_id.max_price, rec.product_uom)
            if rec.proposed_price_unit < min_price or rec.proposed_price_unit > max_price:
                # raise ValidationError('Unit Price for product %s is out of the allowed range' % rec.product_id.name)
                return False
        return True

    def _compute_blanket_qty(self):
        for rec in self:
            rec.blanket_delivered_qty = 0.0

    @api.constrains('price_unit')
    def check_status_before_update_price(self):
        for rec in self:
            if rec.state not in ['draft', 'new']:
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






