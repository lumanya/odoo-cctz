from odoo import fields, models, api


class AssetLocation(models.Model):
    _name = "asset.location"
    _description = "Asset Location"

    name = fields.Char(string="Name")
    is_default = fields.Boolean(string="Default")
    is_scrap = fields.Boolean(string="Scrap")
    asset_line = fields.One2many(comodel_name="asset.detail", inverse_name="location_id")

