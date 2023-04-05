from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    salla_id = fields.Char('Salla ID')
    branch = fields.Selection([]) 
    salla_integration_id = fields.Many2one('integration.salla')
    order_t = fields.Selection([('salla','Salla'),('other','other')],default="other")  
    payment_method = fields.Many2one('salla.payment.method')
    salla_order_date = fields.Datetime()
    salla_state = fields.Selection([('under_review','under review'),('in_progress','in progress'),('completed','completed'),('canceled','canceled'),('payment_pending','payment_pending'),('delivering','delivering'),('delivered','delivered'),('restored','restored'),('restoring','restoring'),('deleted','deleted')])

    def run_create_invoice(self):
        for rec in self:
            inv_wiz = self.env['sale.advance.payment.inv'].create({
                'advance_payment_method':'delivered'

            })

            inv_wiz.create_invoice_custom(rec.id)

    def run_cancel(self):
        for rec in self:
            rec._action_cancel()

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = {
            'ref': order.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'journal_id':order.payment_method.journal_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_reference': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }
    def create_invoice_custom(self,id):
        sale_orders = self.env['sale.order'].browse(id)

        if self.advance_payment_method == 'delivered':
            sale_orders._create_invoices(final=self.deduct_down_payments)

class SaleOrder(models.Model):
    _inherit = "account.move"

    salla_id = fields.Char('OpenCart ID')
    branch = fields.Selection([]) 
    salla_integration_id = fields.Many2one('integration.salla')   
   




   