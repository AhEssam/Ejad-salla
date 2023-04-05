from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "product.template"

    salla_id = fields.Integer('Salla ID')
    branch = fields.Selection([])
    salla_integration_id = fields.Many2one('integration.salla')   
class ProductCategory(models.Model):
     _inherit = "product.category"
     salla_id = fields.Integer('Salla ID')
     branch = fields.Selection([])
     salla_integration_id = fields.Many2one('integration.salla') 
class ProductAttribute(models.Model):
     _inherit = "product.attribute"
     salla_id = fields.Integer('Salla ID')
     branch = fields.Selection([])
     salla_integration_id = fields.Many2one('integration.salla') 
