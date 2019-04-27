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
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            product = self.product_id.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)
        
        pricelist_item_obj = self.env['product.pricelist.item']
#         if self.order_id.pricelist_id.pricelist_type == 'tender':
        pricelist_item_ids = pricelist_item_obj.search([('pricelist_id','=',self.order_id.pricelist_id.id),
                                                        ('product_id','=',product.id)])
        if not pricelist_item_ids:
            pricelist_item_ids = pricelist_item_obj.search([('pricelist_id','=',self.order_id.pricelist_id.id),
                                                            ('product_tmpl_id','=',product.product_tmpl_id.id)])
            
        for pricelist_item in pricelist_item_ids:
            if pricelist_item.uom_id:
                self.update({'product_uom': pricelist_item.uom_id.id})
                     
        uom_list_ids = pricelist_item_ids.mapped('uom_id.id')
        result.get('domain', {}).update({'product_uom': [('id', 'in', uom_list_ids)]})
        
        
        
        return result




    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id.id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position'),
                product = self.product_id.id
            )
            
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)

    def _get_domain(self):
        """
        for a singleton, get the list of allowable uom for the selected product
        the list of allowable uom is taken from the pricelist
        :return: list of id for uom [ , , ]
        """
        self.ensure_one()
        domain = []
        return domain

