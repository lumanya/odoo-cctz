from odoo import fields, models, api
from datetime import datetime


class AssetDetail(models.Model):
    _name = "asset.detail"
    _description = "Asset Detail"

    name = fields.Char(string="Name")
    asset_image = fields.Binary(string="Image")
    category_id = fields.Many2one(comodel_name="asset.category", string="Category")
    asset_code = fields.Char(string="Asset Code")
    asset_model = fields.Char(string="Asset Model")
    serial_no = fields.Char(string="Serial No.")
    purchase_date = fields.Date(string="Purchase Date")
    purchase_value = fields.Float(string="Purchase Value")
    location_id = fields.Many2one(comodel_name="asset.location", string="Current Location")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    vendor_id = fields.Many2one(comodel_name="res.partner", string="Vendor")
    warranty_start = fields.Date(string="Warranty Start")
    warranty_end = fields.Date(string="Warranty End")
    note = fields.Html(string="Note")
    state = fields.Selection([('draft', 'New'), ('active', 'Active'), ('scrap', 'Scrap')], string='State', default="draft")

    @api.model
    def create(self, vals):
        location_id = self.env["asset.location"].search([("is_default", "=", True)], limit=1)
        vals["asset_code"] = self.env["ir.sequence"].next_by_code("asset.detail", sequence_date=datetime.now().year) or "New"
        vals["location_id"] = location_id.id if location_id else None
        return super(AssetDetail, self).create(vals)

    def scrap_asset(self):
        for asset_id in self:
            location_id = self.env["asset.location"].search([("is_scrap", "=", True)], limit=1)
            if location_id:
                asset_id.state = "scrap"

    def confirm_asset(self):
        for asset_id in self:
            asset_id.state = "active"