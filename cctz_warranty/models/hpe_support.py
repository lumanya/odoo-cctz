from odoo import fields, api, models, _
from odoo.exceptions import ValidationError

class HPESupport(models.Model):
    _name = 'hpe.support'
    _description = 'HPE Technician Support'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name_id = fields.Many2one('res.users', string='HPE Technician', tracking=True, required=True)
    passport_code = fields.Char(string="HPE Passport Code")

    def name_get(self):
        result = []
        for record in self:
            if record.name_id:
                name = f"{record.name_id.name}"
                result.append((record.id, name))
        return result

