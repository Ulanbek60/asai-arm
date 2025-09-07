from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError

class ArmTask(models.Model):
    _name = "arm.task"
    _description = "Производственное задание (деталь/операция)"
    _order = "priority desc, id asc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    workcenter_id = fields.Many2one("arm.workcenter", string="Рабочая зона", required=True)

    priority = fields.Selection([
        ("0", "Низкий"),
        ("1", "Нормальный"),
        ("2", "Высокий"),
        ("3", "Критичный"),
    ], default="1", index=True)

    state = fields.Selection([
        ("ready", "Готово к работе"),
        ("in_progress", "В работе"),
        ("done", "Готово"),
        ("scrap", "Брак"),
        ("blocked", "Невозможно выполнить"),
    ], default="ready", tracking=True)

    assigned_user_ids = fields.Many2many(
        "res.users", "arm_task_user_rel", "task_id", "user_id",
        string="Операторы в работе",
    )
    operator_id = fields.Many2one("res.users", string="Завершил")

    scrap_reason_id = fields.Many2one("arm.scrap.reason", string="Причина брака")
    block_reason_id = fields.Many2one("arm.block.reason", string="Причина невозможности")
    block_notes = fields.Char("Комментарий блокировки")

    planned_start = fields.Datetime("План. старт")
    planned_end   = fields.Datetime("План. конец")

    start_time = fields.Datetime("Начало")
    end_time   = fields.Datetime("Окончание")

    duration = fields.Float("Длительность, ч", compute="_compute_duration", store=True)

    active = fields.Boolean(default=True, help="Скрываем из списков после завершения")

    status_label = fields.Char(compute="_compute_status_label")
    is_my_task   = fields.Boolean(compute="_compute_is_my_task")

    @api.depends('state')
    def _compute_status_label(self):
        for rec in self:
            rec.status_label = "В работе:" if rec.state == "in_progress" else ""

    @api.depends('assigned_user_ids')
    def _compute_is_my_task(self):
        uid = self.env.user.id
        for rec in self:
            rec.is_my_task = uid in rec.assigned_user_ids.ids

    # ---- ВАЛИДАЦИИ ДАТ ----
    @api.constrains('start_time', 'end_time')
    def _check_fact_times(self):
        for rec in self:
            if rec.start_time and rec.end_time and rec.end_time < rec.start_time:
                raise ValidationError(_("Окончание не может быть раньше начала."))

    @api.constrains('planned_start', 'planned_end')   # ← правильные имена полей
    def _check_plan_times(self):
        for rec in self:
            if rec.planned_start and rec.planned_end and rec.planned_end < rec.planned_start:
                raise ValidationError(_("Плановое окончание не может быть раньше планового начала."))

    @api.onchange('start_time', 'end_time')
    def _onchange_fact_times(self):
        if self.start_time and self.end_time and self.end_time < self.start_time:
            return {
                'warning': {
                    'title': _("Неверный интервал"),
                    'message': _("Окончание не может быть раньше начала."),
                }
            }

    # ---- ДЛИТЕЛЬНОСТЬ ----
    @api.depends("start_time", "end_time")
    def _compute_duration(self):
        for rec in self:
            if rec.start_time and rec.end_time:
                delta = rec.end_time - rec.start_time
                hours = delta.total_seconds() / 3600.0
                rec.duration = max(hours, 0.0)  # никогда не уходим в минус
            else:
                rec.duration = 0.0


    # ---- Actions ----
    def action_take(self):
        for r in self:
            if self.env.user not in r.assigned_user_ids:
                r.assigned_user_ids = [(4, self.env.user.id)]
            if r.state in ("ready", "blocked"):
                r.state = "in_progress"
                if not r.start_time:
                    r.start_time = fields.Datetime.now()
        return True

    def action_done(self):
        for r in self:
            if r.state != "in_progress":
                raise exceptions.UserError(_("Задание должно быть в работе."))
            r.end_time = fields.Datetime.now()
            r.operator_id = self.env.user
            r.state = "done"
            r.active = False
        return True

    def action_scrap_open(self):
        self.ensure_one()
        if self.state not in ("in_progress", "ready"):
            raise exceptions.UserError(_("Можно забраковать только готовое или выполняемое задание."))
        return {
            "name": _("Указать брак"),
            "type": "ir.actions.act_window",
            "res_model": "arm.scrap.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_task_id": self.id},
        }

    def action_block(self):
        self.ensure_one()
        if self.state in ("done", "scrap", "blocked"):
            raise exceptions.UserError(_("Задание уже завершено или невозможно выполнить."))
        return {
            "name": _("Указать невозможность выполнения"),
            "type": "ir.actions.act_window",
            "res_model": "arm.block.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_task_id": self.id},
        }
