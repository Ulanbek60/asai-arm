from odoo.tests.common import TransactionCase, tagged
from odoo import fields

@tagged('-at_install', 'post_install')
class TestArm(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Workcenter = self.env['arm.workcenter']
        self.Task = self.env['arm.task']
        self.Reason = self.env['arm.scrap.reason']
        self.wc = self.Workcenter.create({'name': 'Тест-Станок'})
        self.reason = self.Reason.create({'name': 'Брак Тест'})
        self.task = self.Task.create({'name': 'T-1', 'workcenter_id': self.wc.id})

    def test_flow(self):
        # take in work
        self.task.action_take()
        self.assertEqual(self.task.state, 'in_progress')
        self.assertTrue(self.task.start_time)
        # scrap via wizard substitute
        self.task.write({'scrap_reason_id': self.reason.id, 'state': 'scrap'})
        self.assertEqual(self.task.state, 'scrap')
        # new task -> done hides row (active=False)
        t2 = self.Task.create({'name': 'T-2', 'workcenter_id': self.wc.id})
        t2.action_take()
        t2.action_done()
        self.assertFalse(t2.active)
