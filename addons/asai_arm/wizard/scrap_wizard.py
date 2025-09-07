from odoo import models, fields

class ArmScrapWizard(models.TransientModel):
    _name = "arm.scrap.wizard"
    _description = "Визард: указание брака"

    task_id = fields.Many2one("arm.task", required=True)
    scrap_reason_id = fields.Many2one("arm.scrap.reason", required=True)
    notes = fields.Char("Комментарий")

    def action_confirm(self):
        self.ensure_one()
        task = self.task_id
        if task.state not in ("in_progress", "ready"):
            return
        task.write({
            "state": "scrap",
            "scrap_reason_id": self.scrap_reason_id.id,
        })
        return {"type": "ir.actions.act_window_close"}
