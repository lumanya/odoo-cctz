from odoo import models, fields, api

class AssetDashboard(models.Model):
    _name = 'asset.dashboard'
    _description = 'Asset Dashboard'
    _auto = False  # We don't store data in this table; it's for display purposes only.

    total_assets = fields.Integer(string="Total Assets")
    total_quantity = fields.Integer(string="Total Quantity")

    @api.model
    def init(self):
        # This method defines a SQL view that computes the total assets and total quantities
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW asset_dashboard AS (
                SELECT
                    1 as id,
                    COUNT(*) as total_assets,
                    SUM(quantity) as total_quantity
                FROM asset_registration
            )
        """)
