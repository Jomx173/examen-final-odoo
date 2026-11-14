from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class UnicahPrestamo(models.Model):
    _name = "unicah.prestamo"
    _description = "Préstamo de equipo"
    _order = "fecha_prestamo desc, id desc"

    name = fields.Char(string="Referencia", default="Nuevo", required=True)
    solicitante_id = fields.Many2one(
        "res.partner",
        string="Solicitante",
        required=True,
    )
    equipo_id = fields.Many2one(
        "unicah.equipo",
        string="Equipo",
        required=True,
    )
    fecha_prestamo = fields.Date(
        string="Fecha de préstamo",
        required=True,
        default=fields.Date.context_today,
    )
    fecha_devolucion = fields.Date(string="Fecha de devolución")
    estado = fields.Selection(
        [
            ("borrador", "Borrador"),
            ("prestado", "Prestado"),
            ("devuelto", "Devuelto"),
        ],
        string="Estado",
        default="borrador",
        required=True,
    )
    observaciones = fields.Text(string="Observaciones")
    dias = fields.Integer(
        string="Días del préstamo",
        compute="_compute_dias",
        store=True,
    )

    @api.depends("fecha_prestamo", "fecha_devolucion")
    def _compute_dias(self):
        for prestamo in self:
            if prestamo.fecha_prestamo and prestamo.fecha_devolucion:
                delta = prestamo.fecha_devolucion - prestamo.fecha_prestamo
                prestamo.dias = max(delta.days, 0)
            else:
                prestamo.dias = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == "Nuevo":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("unicah.prestamo") or "Nuevo"
                )
        return super().create(vals_list)

    @api.constrains("fecha_prestamo", "fecha_devolucion")
    def _check_fechas(self):
        for prestamo in self:
            if (
                prestamo.fecha_devolucion
                and prestamo.fecha_devolucion < prestamo.fecha_prestamo
            ):
                raise ValidationError(
                    "La fecha de devolución no puede ser anterior a la fecha de préstamo."
                )

    def action_prestar(self):
        for prestamo in self:
            if prestamo.estado != "borrador":
                raise UserError("Solo un préstamo en borrador puede entregarse.")
            ocupado = self.search_count(
                [
                    ("equipo_id", "=", prestamo.equipo_id.id),
                    ("estado", "=", "prestado"),
                    ("id", "!=", prestamo.id),
                ]
            )
            if ocupado:
                raise UserError(
                    "El equipo %s ya tiene un préstamo activo." % prestamo.equipo_id.name
                )
            prestamo.estado = "prestado"

    def action_devolver(self):
        for prestamo in self:
            if prestamo.estado != "prestado":
                raise UserError("Solo un equipo prestado puede devolverse.")
            prestamo.estado = "devuelto"
