# -*- coding: utf-8 -*-
# from odoo import http


# class AssetManagement(http.Controller):
#     @http.route('/asset_management/asset_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/asset_management/asset_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('asset_management.listing', {
#             'root': '/asset_management/asset_management',
#             'objects': http.request.env['asset_management.asset_management'].search([]),
#         })

#     @http.route('/asset_management/asset_management/objects/<model("asset_management.asset_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('asset_management.object', {
#             'object': obj
#         })
