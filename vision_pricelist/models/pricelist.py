# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from itertools import chain


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    pricelist_type = fields.Selection([('public', 'Public'),
                                       ('tender', 'Tender')], string='Type', default='public')
    partner_ids = fields.One2many('res.partner', 'property_product_pricelist', 'Customer')
    assign_button_visible = fields.Boolean('Assign partner button visible', compute='_compute_button_visible')
    remove_button_visible = fields.Boolean('Remove button visible', compute='_compute_remove_button_visible')

    # @api.constrains('pricelist_type')
    # def _check_pricelist_rules(self):
    #     to_do_ids = self.filtered(lambda r: r.pricelist_type == 'tender')
    #     for rec in to_do_ids:
    #         rule_ids = rec.item_ids
    #         bad_ids = rule_ids.filtered(
    #             lambda r: r.applied_on != '0_product_variant' or not r.uom_id or r.compute_price != 'fixed')
    #
    #         if len(bad_ids) > 0:
    #             raise UserError('All rules in a tender pricelist must be assigned to a specific product with a fixed price')

    @api.depends('partner_ids')
    def _compute_remove_button_visible(self):
        for rec in self:
            rec.remove_button_visible = len(rec.partner_ids) > 0

    @api.depends('pricelist_type', 'partner_ids')
    def _compute_button_visible(self):
        for rec in self:
            rec.assign_button_visible = rec.pricelist_type == 'tender' and len(rec.partner_ids) == 0

    @api.multi
    def action_assign_partner(self):
        self.ensure_one()
        action = {
            "name": "Assign a Customer",
            "type": "ir.actions.act_window",
            "res_model": "assign.pricelist.partner",
            "views": [[False, "form"]],
            "context": {'default_pricelist_id': self.id},
            "target": 'new',
        }
        return action

    @api.multi
    def action_remove_partner(self):
        self.ensure_one()
        action = {
            "name": "Re-Assign Customer(s)",
            "type": "ir.actions.act_window",
            "res_model": "remove.pricelist.partner",
            "views": [[False, "form"]],
            "context": {'default_pricelist_id': self.id},
            "target": 'new',
        }
        return action

    @api.multi
    def assign_partner(self, partner_id):
        self.ensure_one()
        if not partner_id:
            return
        partner_id.write({'property_product_pricelist': self.id})

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        If date in context: Date of the pricelist (%Y-%m-%d)

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.context_today(self)
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        if not uom_id:
            self._cr.execute(
                'SELECT item.id '
                'FROM product_pricelist_item AS item '
                'LEFT JOIN product_category AS categ '
                'ON item.categ_id = categ.id '
                'WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))'
                'AND (item.product_id IS NULL OR item.product_id = any(%s))'
                'AND (item.categ_id IS NULL OR item.categ_id = any(%s)) '
                'AND (item.pricelist_id = %s) '
                'AND (item.date_start IS NULL OR item.date_start<=%s) '
                'AND (item.date_end IS NULL OR item.date_end>=%s)'
                'ORDER BY item.applied_on, item.min_quantity desc, categ.parent_left desc',
                (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))
        else:
            self._cr.execute(
                'SELECT item.id '
                'FROM product_pricelist_item AS item '
                'LEFT JOIN product_category AS categ '
                'ON item.categ_id = categ.id '
                'WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))'
                'AND (item.product_id IS NULL OR item.product_id = any(%s))'
                'AND (item.categ_id IS NULL OR item.categ_id = any(%s)) '
                'AND (item.pricelist_id = %s) '
                'AND (item.date_start IS NULL OR item.date_start<=%s) '
                'AND (item.date_end IS NULL OR item.date_end>=%s)'
                'AND (item.uom_id IS NULL OR item.uom_id = %s ) '
                'ORDER BY item.applied_on, item.min_quantity desc, categ.parent_left desc',
                (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date, uom_id))

        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.env['product.pricelist.item'].browse(item_ids)
        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['product.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute('list_price')[product.id]

            price_uom = self.env['product.uom'].browse([qty_uom_id])
            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)])[product.id][0]  # TDE: 0 = price, 1 = rule
                    price = rule.base_pricelist_id.currency_id.compute(price_tmp, self.currency_id, round=False)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]

                convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'percentage':
                        price = (price - (price * (rule.percent_price / 100))) or 0.0
                    else:
                        # complete formula
                        price_limit = price
                        price = (price - (price * (rule.price_discount / 100))) or 0.0
                        if rule.price_round:
                            price = tools.float_round(price, precision_rounding=rule.price_round)

                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(rule.price_surcharge)
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(rule.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(rule.price_max_margin)
                            price = min(price, price_limit + price_max_margin)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                price = product.currency_id.compute(price, self.currency_id, round=False)

            results[product.id] = (price, suitable_rule and suitable_rule.id or False)

        return results


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    uom_id = fields.Many2one('product.uom', 'Unit of Measure')

    @api.onchange('applied_on')
    def onchange_update_uom(self):
        self.ensure_one()
        if self.applied_on in ['3_global', '2_product_category']:
            self.uom_id = False

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.ensure_one()
        domain = {'uom_id': []}
        if self.product_id:
            domain.update({'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]})
        result = {'domain': domain}
        return result

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        self.ensure_one()
        domain = {'uom_id': []}
        if self.product_tmpl_id:
            domain.update({'uom_id': [('category_id', '=', self.product_tmpl_id.uom_id.category_id.id)]})
        result = {'domain': domain}
        return result


class ProductUoM(models.Model):
    _inherit = 'product.uom'

    @api.multi
    def _compute_price(self, price, to_unit):
        ctx = dict(self._context or {})
        if ctx.get('pricelist', False) and ctx.get('product', False) and to_unit:
            pricelist_item_obj = self.env['product.pricelist.item']
            pricelist_brw = self.env['product.pricelist'].browse(ctx.get('pricelist'))
            #             if pricelist_brw.pricelist_type == 'tender':
            pricelist_item_ids = pricelist_item_obj.search([('pricelist_id', '=', pricelist_brw.id),
                                                            ('product_id', '=', ctx.get('product')),
                                                            ('uom_id', '=', to_unit.id)])
            if not pricelist_item_ids:
                product_tmpl = self.env['product.product'].browse(ctx.get('product')).product_tmpl_id
                pricelist_item_ids = pricelist_item_obj.search([('pricelist_id', '=', pricelist_brw.id),
                                                                ('product_tmpl_id', '=', product_tmpl.id),
                                                                ('uom_id', '=', to_unit.id)])
            if pricelist_item_ids:
                return price

        self.ensure_one()
        if not self or not price or not to_unit or self == to_unit:
            return price
        if self.category_id.id != to_unit.category_id.id:
            return price
        amount = price * self.factor
        if to_unit:
            amount = amount / to_unit.factor
        return amount

