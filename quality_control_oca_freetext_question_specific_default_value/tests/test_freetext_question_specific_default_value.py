from odoo.addons.base.tests.common import BaseCommon


class TestFreetextQuestionSpecificDefaultValue(BaseCommon):
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
                "name": "Comments",
                "test": cls.test.id,
                "type": "freetext",
            }
        )

    def _prepare_line(self):
        return self.inspection_model._prepare_inspection_line(
            self.test, self.question, fill=self.test.fill_correct_values
        )

    def test_pre_fill_leaves_empty_when_specific_value_disabled(self):
        self.question.use_specific_default_freetext_value = False
        data = self._prepare_line()
        self.assertNotIn("freetext_value", data)

    def test_pre_fill_uses_specific_value_when_enabled(self):
        self.question.write(
            {
                "use_specific_default_freetext_value": True,
                "default_freetext_value": "Looks good",
            }
        )
        data = self._prepare_line()
        self.assertEqual(data["freetext_value"], "Looks good")

    def test_no_pre_fill_when_fill_disabled(self):
        self.test.fill_correct_values = False
        self.question.write(
            {
                "use_specific_default_freetext_value": True,
                "default_freetext_value": "Looks good",
            }
        )
        data = self.inspection_model._prepare_inspection_line(
            self.test, self.question, fill=self.test.fill_correct_values
        )
        self.assertNotIn("freetext_value", data)
