from odoo import fields, models


class UnicahEquipo(models.Model):
    _name = "unicah.equipo"
    _description = "Equipo de la universidad"

    name = fields.Char(string="Nombre", required=True)
    codigo = fields.Char(string="Código", required=True)
    tipo = fields.Selection(
        [
            ("proyector", "Proyector"),
            ("laptop", "Laptop"),
            ("microfono", "Micrófono"),
            ("otro", "Otro"),
        ],
        string="Tipo",
        required=True,
    )
    ubicacion = fields.Char(string="Ubicación")
    prestamo_ids = fields.One2many(
        "unicah.prestamo",
        "equipo_id",
        string="Préstamos",
    )
