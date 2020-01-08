# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo import tools


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, help="Pricelist for current sales order Line.")
    filter_all_product = fields.Boolean("Filter All Product", default=False)
    
    @api.onchange('filter_all_product')
    def onchange_filter_all_product(self):
        if self.filter_all_product:
            return {'domain': {'product_id':[]}}
        if not self.filter_all_product:
            product_obj = self.env['product.product']
            if self.pricelist_id:
                product_lst_ids = []
                pricilist_template_ids = self.pricelist_id.item_ids.search([('applied_on', '=', '1_product'), ('pricelist_id', '=', self.pricelist_id.id)])
                if pricilist_template_ids:
                    product_variant_ids = product_obj.search([('product_tmpl_id', 'in', pricilist_template_ids.mapped('product_tmpl_id.id'))])
                    product_lst_ids.extend(product_variant_ids.mapped('id'))
                pricilist_product_ids = self.pricelist_id.item_ids.search([('applied_on', '=', '0_product_variant'), ('pricelist_id', '=', self.pricelist_id.id)])
                if pricilist_product_ids:
                    product_lst_ids.extend(pricilist_product_ids.mapped('product_id.id'))
                return {'domain': {'product_id': [('id', 'in', product_lst_ids)]}}
    
    @api.depends('price_unit', 'proposed_price_unit', 'pricelist_id')
    def _check_line(self):
        super(SaleOrderLine, self)._check_line()
        for rec in self:
            rec.line_ok = rec.line_ok and rec._check_price_with_pricelist()
        return

    def _check_price_with_pricelist(self):
        self.ensure_one()
        res = True
        if self.pricelist_id and self.pricelist_id.pricelist_type == 'tender':
            res = self.proposed_price_unit == self.price_unit
        return res

    @api.multi
    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        pricelist_id = self.pricelist_id
        if not pricelist_id:
            pricelist_id = self.order_id.pricelist_id
            
        if pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)
        final_price, rule_id = pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        base_price, currency_id = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, pricelist_id.id)
        if currency_id != pricelist_id.currency_id.id:
            base_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(base_price, pricelist_id.currency_id)
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.multi
    @api.onchange('product_id', 'pricelist_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        vals = {}
        pricelist_id = self.pricelist_id
        if not pricelist_id:
            pricelist_id = self.order_id.pricelist_id
        
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=pricelist_id.id,
            uom=self.product_uom.id,
            product=self.product_id.id
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

        if pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        pricelist_item_obj = self.env['product.pricelist.item']
        #         if pricelist_id.pricelist_type == 'tender':
        pricelist_item_ids = pricelist_item_obj.search([('pricelist_id', '=', pricelist_id.id),
                                                        ('product_id', '=', product.id)])
        if not pricelist_item_ids:
            pricelist_item_ids = pricelist_item_obj.search([('pricelist_id', '=', pricelist_id.id),
                                                            ('product_tmpl_id', '=', product.product_tmpl_id.id)])

        for pricelist_item in pricelist_item_ids:
            if pricelist_item.uom_id:
                self.update({'product_uom': pricelist_item.uom_id.id})

        uom_list_ids = pricelist_item_ids.mapped('uom_id.id')
        result.get('domain', {}).update({'product_uom': [('id', 'in', uom_list_ids)]})

        return result

    @api.onchange('product_uom', 'product_uom_qty','pricelist_id')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        
        pricelist_id = self.pricelist_id
        if not pricelist_id:
            pricelist_id = self.order_id.pricelist_id
            
        if pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id.id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position'),
                product=self.product_id.id
            )

            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                      product.taxes_id, self.tax_id,
                                                                                      self.company_id)

    def _get_domain(self):
        """
        for a singleton, get the list of allowable uom for the selected product
        the list of allowable uom is taken from the pricelist
        :return: list of id for uom [ , , ]
        """
        self.ensure_one()
        domain = []
        return domain