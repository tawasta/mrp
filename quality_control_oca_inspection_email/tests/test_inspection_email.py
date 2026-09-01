from odoo.addons.base.tests.common import BaseCommon


class TestInspectionEmail(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection_model = cls.env["qc.inspection"]
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.inspection = cls.inspection_model.create({"name": "Test Inspection"})

    def test_action_send_by_email_context(self):
        action = self.inspection.action_send_by_email()
        self.assertEqual(action["res_model"], "mail.compose.message")
        ctx = action["context"]
        self.assertEqual(ctx["default_res_ids"], self.inspection.ids)
        self.assertTrue(ctx["mark_qc_inspection_email_as_sent"])
        self.assertIn("default_template_id", ctx)
        self.assertNotIn("default_partner_ids", ctx)

    def test_partner_id_is_mail_partner(self):
        self.inspection.partner_id = self.partner
        self.assertEqual(
            self.inspection._mail_get_partners()[self.inspection.id],
            self.partner,
        )

    def test_template_partner_to_targets_partner_id(self):
        template = self.env.ref(
            "quality_control_oca_inspection_email.mail_template_qc_inspection"
        )
        self.assertEqual(template.partner_to, "{{ object.partner_id.id }}")

    def test_message_post_marks_email_sent(self):
        self.assertFalse(self.inspection.inspection_email_sent)
        self.inspection.with_context(
            mark_qc_inspection_email_as_sent=True
        ).message_post(body="Test message")
        self.assertTrue(self.inspection.inspection_email_sent)

    def test_message_post_without_context_does_not_mark_sent(self):
        self.inspection.message_post(body="Test message")
        self.assertFalse(self.inspection.inspection_email_sent)
