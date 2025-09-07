from odoo import models, fields

class ArmScrapReason(models.Model):
    _name = "arm.scrap.reason"
    _description = "Причина брака"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

class ArmBlockReason(models.Model):
    _name = "arm.block.reason"
    _description = "Причина невозможности выполнения"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
