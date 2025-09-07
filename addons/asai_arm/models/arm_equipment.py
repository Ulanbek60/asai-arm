from odoo import models, fields

class ArmWorkcenter(models.Model):
    _name = "arm.workcenter"
    _description = "Рабочая зона/станок"

    name = fields.Char(required=True)
    code = fields.Char()
    is_active = fields.Boolean(default=True)

class ArmMaintenance(models.Model):
    _name = "arm.maintenance"
    _description = "Обслуживание оборудования"
    _order = "date desc"

    workcenter_id = fields.Many2one("arm.workcenter", required=True)
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    type = fields.Selection([
        ("planned", "Плановое"),
        ("replace", "Замена"),
        ("breakdown", "Поломка"),
    ], default="planned", required=True)
    notes = fields.Text()
    user_id = fields.Many2one("res.users", default=lambda s: s.env.user)
