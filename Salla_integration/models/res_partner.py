from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    salla_id = fields.Char('OpenCart ID')
    branch = fields.Selection([])
    salla_integration_id = fields.Many2one('integration.salla')