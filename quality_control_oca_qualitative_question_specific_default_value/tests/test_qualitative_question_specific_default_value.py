from odoo import exceptions

from odoo.addons.base.tests.common import BaseCommon


class TestQualitativeQuestionSpecificDefaultValue(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection_model = cls.env["qc.inspection"]
        cls.test = cls.env["qc.test"].create(
            {
                "name": "Generic Test",
                "fill_correct_values": True,
            }
        )
        cls.question = cls.env["qc.test.question"].create(
            {
                "name": "Overall quality",
                "test": cls.test.id,
                "type": "qualitative",
            }
        )
        cls.val_ok_first = cls.env["qc.test.question.value"].create(
            {"name": "Good", "ok": True, "test_line": cls.question.id}
        )
        cls.val_ok_second = cls.env["qc.test.question.value"].create(
            {"name": "Excellent", "ok": True, "test_line": cls.question.id}
        )
        cls.val_ko = cls.env["qc.test.question.value"].create(
            {"name": "Bad", "ok": False, "test_line": cls.question.id}
        )

    def _prepare_line(self):
        return self.inspection_model._prepare_inspection_line(
            self.test, self.question, fill=self.test.fill_correct_values
        )

    def test_pre_fill_uses_first_correct_value_when_none_flagged(self):
        data = self._prepare_line()
        self.assertEqual(data["qualitative_value"], self.val_ok_first.id)

    def test_pre_fill_uses_flagged_value_when_set(self):
        self.val_ok_second.is_default_qualitative_value = True
        data = self._prepare_line()
        self.assertEqual(data["qualitative_value"], self.val_ok_second.id)

    def test_no_pre_fill_when_fill_disabled(self):
        self.test.fill_correct_values = False
        self.val_ok_second.is_default_qualitative_value = True
        data = self.inspection_model._prepare_inspection_line(
            self.test, self.question, fill=self.test.fill_correct_values
        )
        self.assertNotIn("qualitative_value", data)

    def test_cannot_flag_incorrect_value_as_default(self):
        with self.assertRaises(exceptions.ValidationError):
            self.val_ko.is_default_qualitative_value = True

    def test_cannot_flag_more_than_one_default_value(self):
        self.val_ok_first.is_default_qualitative_value = True
        with self.assertRaises(exceptions.ValidationError):
            self.val_ok_second.is_default_qualitative_value = True
