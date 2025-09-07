from odoo import models, fields

class ArmBlockWizard(models.TransientModel):
    _name = "arm.block.wizard"
    _description = "Визард: невозможно выполнить"

    task_id = fields.Many2one("arm.task", string="Задание", required=True, readonly=True)
    block_reason_id = fields.Many2one("arm.block.reason", string="Причина невозможности", required=True)
    notes = fields.Char("Комментарий")

    def action_confirm(self):
        self.ensure_one()
        task = self.task_id
        task.block_reason_id = self.block_reason_id
        task.block_notes = self.notes
        task.state = "blocked"
        return {"type": "ir.actions.act_window_close"}
