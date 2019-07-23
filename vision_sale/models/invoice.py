# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import base64
from io import StringIO, BytesIO
import xlwt
import xlsxwriter

class InvoiceCostReport(models.TransientModel):
    _name = 'invoice.cost.report'

    datas = fields.Binary('File')
    datas_fname = fields.Char(string='File Name')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    portal_requester = fields.Char('Portal Requester')
    portal_requester_info = fields.Char('Portal Requester info')
    portal_requester_id = fields.Char('Portal Requester ID')
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

    @api.multi
    def action_report_1(self):

        created_file_path = '/tmp/Cost Center Report Invoice %s.xlsx' % (self.name or '')
        workbook = xlsxwriter.Workbook(created_file_path)
        worksheet = workbook.add_worksheet()
        header = workbook.add_format({'bold': 1, 'align': 'left'})
        align = workbook.add_format({'align': 'left'})
        merge_format = workbook.add_format({
                                            'bold': 1,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter',
                                            })
        border_formater = workbook.add_format({'border':1})
        num_format = workbook.add_format({'num_format': '###0.00'})
        title = "Cost Center Report of Invoice %s" % (self.name)
        worksheet.merge_range('A1:E1', title, merge_format)


        worksheet.merge_range(3,1,3,3, "Invoice Number %s"%(str(self.name or 'DRAFT')), merge_format)

        row = first_row = 7
        worksheet.set_column(0, 3, 14)
        worksheet.set_row(row, 28)
        
        worksheet.write(row, 0, "Cost Center", header)
        worksheet.write(row, 1, "Requester ID", header)
        worksheet.write(row , 2, "Amount \n (Before Tax)", header)
        

        for ln in self.grouped_line_ids:
            worksheet.write(row + 1, 0, ln.summary_by, align)
            worksheet.write(row + 1, 1, self.portal_requester_id, align)
            worksheet.write(row + 1, 2, ln.price_total, num_format)
            row += 1
# 
        worksheet.conditional_format(first_row, 0, row, 3,{'type' : 'no_blanks','format':border_formater})
        workbook.close()
        file = open(created_file_path, 'rb')
        report_data_file = base64.encodebytes(file.read())
        file.close()
        
        report_id = self.env['invoice.cost.report'].create({'datas': report_data_file,
                    'datas_fname': 'Cost Report of Invoice %s.xlsx' % (self.name),
                    'show_datas': True})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice Cost Report',
            'res_model': 'invoice.cost.report',
            'res_id': report_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }    

    
    @api.multi
    def action_report_2(self):
        inv_ln_obj = self.env['account.invoice.line']

        created_file_path = '/tmp/Cost Center Report Invoice %s.xlsx' % (self.name or '')
        workbook = xlsxwriter.Workbook(created_file_path)
        worksheet = workbook.add_worksheet()
        header = workbook.add_format({'bold': 1, 'align': 'left'})
        align = workbook.add_format({'align': 'left'})
        merge_format = workbook.add_format({
                                            'bold': 1,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter',
                                            })
        border_formater = workbook.add_format({'border':1})
        num_format = workbook.add_format({'num_format': '###0.00'})
        title = "Cost Center Report of Invoice %s" % (self.name)
        worksheet.merge_range('A1:E1', title, merge_format)


        worksheet.merge_range(3,1,3,3, "Invoice Number %s"%(str(self.name or 'DRAFT')), merge_format)

# 
        row = first_row = 7
        worksheet.set_column(0, 3, 14)
        worksheet.set_row(row, 28)
        
        worksheet.write(row, 0, "Cost Center", header)
        worksheet.write(row, 1, "Requester ID", header)
        worksheet.write(row ,2, "List Of SO", header)
        worksheet.write(row ,3, "SO Amount", header)
        

        to_do = self._cost_center_line()
        main_list =[]
        so_dict = {}
        for cost_center, line_list in to_do.items():
            for inv_ln  in inv_ln_obj.browse(line_list):
                if inv_ln.sale_order_id and (inv_ln.sale_order_id.id not in so_dict):
                    so_dict[inv_ln.sale_order_id.id]= [cost_center, inv_ln.sale_order_id.name, inv_ln.sale_order_id.portal_requester_id, inv_ln.sale_order_id.amount_untaxed]
                    cost_center = '' #to print only one time cost center name
                    
        for so_id, cost_lst in so_dict.items():
            worksheet.write(row + 1, 0, cost_lst[0], align) #cost ceter
            worksheet.write(row + 1, 1, cost_lst[2], align) #portal request ID
            worksheet.write(row + 1, 2, cost_lst[1], align) #SO name
            worksheet.write(row + 1, 3, cost_lst[3], num_format) #SO Amount
            row += 1

        worksheet.conditional_format(first_row, 0, row, 4,{'type' : 'no_blanks','format':border_formater})
        workbook.close()
        file = open(created_file_path, 'rb')
        report_data_file = base64.encodebytes(file.read())
        file.close()
        report_id = self.env['invoice.cost.report'].create({'datas': report_data_file,
                    'datas_fname': 'Cost Report of Invoice %s.xlsx' % (self.name),
                    'show_datas': True})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice Cost Report',
            'res_model': 'invoice.cost.report',
            'res_id': report_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }    
    

    @api.multi
    def action_report_3(self):
        inv_ln_obj = self.env['account.invoice.line']

        created_file_path = '/tmp/Cost Center Report Invoice %s.xlsx' % (self.name or '')
        workbook = xlsxwriter.Workbook(created_file_path)
        worksheet = workbook.add_worksheet()
        header = workbook.add_format({'bold': 1, 'align': 'left'})
        align = workbook.add_format({'align': 'left'})
        merge_format = workbook.add_format({
                                            'bold': 1,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter',
                                            })
        border_formater = workbook.add_format({'border':1})
        num_format = workbook.add_format({'num_format': '###0.00'})
        title = "Cost Center Report of Invoice %s" % (self.name)
        worksheet.merge_range('A1:E1', title, merge_format)


        worksheet.merge_range(3,1,3,3, "Invoice Number %s"%(str(self.name or 'DRAFT')), merge_format)
        worksheet.merge_range(4,1,4,3, "Category Of Order : %s"%(str(self.order_customer_category or '')), merge_format)

        row = first_row = 7
        worksheet.set_column(0, 3, 14)
        worksheet.set_row(row, 28)
        
        worksheet.write(row, 0, "Cost Center", header)
        worksheet.write(row, 1, "Requester ID", header)
        worksheet.write(row ,2, "List Of SO", header)
        worksheet.write(row ,3, "Product Code", header)
        worksheet.write(row ,4, "Product Description", header)
        worksheet.write(row ,5, "Uom", header)
        

        to_do = self._cost_center_line()
        main_list =[]
        so_dict = {}
        cost_center_flag = ''
        for cost_center, line_list in to_do.items():
            for inv_ln  in inv_ln_obj.browse(line_list):
                if inv_ln.sale_order_id and (inv_ln.sale_order_id.id not in so_dict):
                    so_dict[inv_ln.sale_order_id.id]= [(cost_center, inv_ln.sale_order_id.portal_requester_id, inv_ln.sale_order_id.name, inv_ln.product_id.default_code, inv_ln.product_id.name, inv_ln.uom_id.name)]
                else:
                    so_dict[inv_ln.sale_order_id.id].append((' ', ' ', inv_ln.sale_order_id.name, inv_ln.product_id.default_code, inv_ln.product_id.name, inv_ln.uom_id.name))
                cost_center =''
        for so_id, cost_lst in so_dict.items():
            for cost_line in cost_lst:
                worksheet.write(row + 1, 0, cost_line[0], align) #cost ceter
                worksheet.write(row + 1, 1, cost_line[1], align) #portal request ID
                worksheet.write(row + 1, 2, cost_line[2], align) #SO name
                worksheet.write(row + 1, 3, cost_line[3], align) #product code
                worksheet.write(row + 1, 4, cost_line[4], align) # product description
                worksheet.write(row + 1, 5, cost_line[5], align) # UOM
                row += 1

        worksheet.conditional_format(first_row, 0, row, 6,{'type' : 'no_blanks','format':border_formater})
        workbook.close()
        file = open(created_file_path, 'rb')
        report_data_file = base64.encodebytes(file.read())
        file.close()
        report_id = self.env['invoice.cost.report'].create({'datas': report_data_file,
                    'datas_fname': 'Cost Report of Invoice %s.xlsx' % (self.name),
                    'show_datas': True})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice Cost Report',
            'res_model': 'invoice.cost.report',
            'res_id': report_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }    
    

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
