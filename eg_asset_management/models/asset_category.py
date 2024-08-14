from odoo import fields, models, api


class AssetCategory(models.Model):
    _name = "asset.category"
    _description = "Asset Category"

    name = fields.Char(string="Name")