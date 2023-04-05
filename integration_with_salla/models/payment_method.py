from odoo import api, fields, models


class SaleOrder(models.Model):
    _name = "salla.payment.method"

    name = fields.Char('')
    journal_id = fields.Many2one('account.journal') 
