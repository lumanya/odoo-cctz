from odoo import models, fields, api

class AssetDashboard(models.Model):
    _name = 'asset.dashboard'
    _description = 'Asset Dashboard'
    _auto = False 

    total_assets = fields.Integer(string="Total Assets")
    total_quantity = fields.Integer(string="Total Quantity")
    fully_depreciated_count = fields.Integer(string="Fully Depreciated Assets")
    non_depreciated_count = fields.Integer(string="Non-Depreciated Assets")


    @api.model
    def init(self):
        # This method defines a SQL view that computes the total assets and total quantities
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW asset_dashboard AS (
                SELECT
                    1 as id,
                    COUNT(*) as total_assets,
                    SUM(quantity) as total_quantity,
                    COUNT(CASE WHEN net_book_value = 0.0 THEN 1 END) as fully_depreciated_count,
                    COUNT(CASE WHEN net_book_value > 0.0 THEN 1 END) as non_depreciated_count
                FROM asset_registration
            )
        """)
