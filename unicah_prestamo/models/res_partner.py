from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    prestamo_ids = fields.One2many(
        "unicah.prestamo",
        "solicitante_id",
        string="Préstamos",
    )
    prestamo_count = fields.Integer(
        string="Préstamos",
        compute="_compute_prestamo_count",
    )

    def _compute_prestamo_count(self):
        for partner in self:
            partner.prestamo_count = len(partner.prestamo_ids)

    def action_ver_prestamos(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Préstamos de %s" % self.name,
            "res_model": "unicah.prestamo",
            "view_mode": "list,form",
            "domain": [("solicitante_id", "=", self.id)],
        }
