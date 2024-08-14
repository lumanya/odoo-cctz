from odoo import fields, models, api
from datetime import datetime


class AssetMove(models.Model):
    _name = "asset.move"
    _description = "Asset Move"

    name = fields.Char(string="Name")
    location_id = fields.Many2one(comodel_name="asset.location", string="Source Location")
    location_dest_id = fields.Many2one(comodel_name="asset.location", string="Destination Location")
    asset_id = fields.Many2one(comodel_name="asset.detail", string="Asset")
    state = fields.Selection([('draft', 'Draft'),('done', 'Done'),('cancel', 'Cancel')], string='State', default="draft")

    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code("asset.move", sequence_date=datetime.now().year) or "New"
        return super(AssetMove, self).create(vals)

    @api.onchange("asset_id")
    def onchange_asset(self):
        self.location_id = self.asset_id.location_id.id

    def move_asset(self):
        for asset_id in self:
            asset_id.asset_id.location_id = asset_id.location_dest_id.id
            asset_id.state = "done"

    def cancel_move(self):
        for asset_id in self:
            asset_id.state = "cancel"