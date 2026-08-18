from odoo.addons.base.tests.common import BaseCommon


class TestQuantitativeQuestionSpecificDefaultValue(BaseCommon):
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
                "name": "Size",
                "test": cls.test.id,
                "type": "quantitative",
                "min_value": 1.0,
                "max_value": 10.0,
            }
        )

    def _prepare_line(self):
        return self.inspection_model._prepare_inspection_line(
            self.test, self.question, fill=self.test.fill_correct_values
        )

    def test_pre_fill_uses_midpoint_when_specific_value_disabled(self):
        self.question.use_specific_default_value = False
        data = self._prepare_line()
        self.assertEqual(data["quantitative_value"], 5.5)

    def test_pre_fill_uses_specific_value_when_enabled(self):
        self.question.write(
            {
                "use_specific_default_value": True,
                "default_quantitative_value": 7.0,
            }
        )
        data = self._prepare_line()
        self.assertEqual(data["quantitative_value"], 7.0)

    def test_pre_fill_uses_specific_value_of_zero(self):
        self.question.write(
            {
                "use_specific_default_value": True,
                "default_quantitative_value": 0.0,
            }
        )
        data = self._prepare_line()
        self.assertEqual(data["quantitative_value"], 0.0)

    def test_no_pre_fill_when_fill_disabled(self):
        self.test.fill_correct_values = False
        self.question.write(
            {
                "use_specific_default_value": True,
                "default_quantitative_value": 7.0,
            }
        )
        data = self.inspection_model._prepare_inspection_line(
            self.test, self.question, fill=self.test.fill_correct_values
        )
        self.assertNotIn("quantitative_value", data)
