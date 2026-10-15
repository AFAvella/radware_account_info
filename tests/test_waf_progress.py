import unittest

import pandas as pd

from modules.waf_progress import (
    calculate_waf_progress,
    classify_feature_state,
    is_enabled,
)


class WafProgressTests(unittest.TestCase):
    def test_three_fully_protected_apps_are_full_progress_and_use_30_percent_capacity(self):
        adoption = pd.DataFrame([
            {"Application Name": f"App {index}", "Application ID": str(index),
             "SQL Injection": "BLOCK", "API Discovery": True}
            for index in range(3)
        ])

        result = calculate_waf_progress(
            adoption,
            ["SQL Injection", "API Discovery"],
            blocking_modules=["SQL Injection"],
            application_ids=["0", "1", "2"],
            application_capacity=10,
        )

        self.assertEqual(result["progress_percent"], 100.0)
        self.assertEqual(result["capacity_percent"], 30.0)
        self.assertEqual(result["expected_checks"], 6)
        self.assertEqual(result["completed_checks"], 6)

    def test_report_only_does_not_meet_a_blocking_requirement(self):
        adoption = pd.DataFrame([{
            "Application Name": "App",
            "Application ID": "1",
            "SQL Injection": "REPORT_ONLY",
        }])

        result = calculate_waf_progress(
            adoption,
            ["SQL Injection"],
            blocking_modules=["SQL Injection"],
            application_ids=["1"],
        )

        self.assertEqual(result["progress_percent"], 0.0)
        self.assertEqual(result["missing_checks"], 1)
        self.assertEqual(result["unknown_checks"], 0)

    def test_unknown_state_stays_unconfirmed_and_in_the_denominator(self):
        adoption = pd.DataFrame([{
            "Application Name": "App",
            "Application ID": "1",
            "SQL Injection": "BLOCK",
            "API Protection": "N/A",
        }])

        result = calculate_waf_progress(
            adoption,
            ["SQL Injection", "API Protection"],
            blocking_modules=["SQL Injection", "API Protection"],
            application_ids=["1"],
        )

        self.assertEqual(result["progress_percent"], 50.0)
        self.assertEqual(result["unknown_checks"], 1)
        self.assertEqual(result["expected_checks"], 2)

    def test_duplicate_application_ids_are_counted_once(self):
        adoption = pd.DataFrame([
            {"Application Name": "App", "Application ID": "1", "SQL Injection": "BLOCK"},
            {"Application Name": "App duplicate", "Application ID": "1", "SQL Injection": "DISABLED"},
        ])

        result = calculate_waf_progress(
            adoption,
            ["SQL Injection"],
            blocking_modules=["SQL Injection"],
        )

        self.assertEqual(result["application_count"], 1)
        self.assertEqual(result["expected_checks"], 1)
        self.assertEqual(result["progress_percent"], 100.0)

    def test_not_configured_is_disabled_not_enabled(self):
        self.assertEqual(classify_feature_state("Not Configured"), "disabled")
        self.assertFalse(is_enabled("Not Configured"))

    def test_no_apps_or_features_has_no_percentage(self):
        result = calculate_waf_progress(
            pd.DataFrame(columns=["Application Name", "Application ID"]),
            ["SQL Injection"],
            application_ids=[],
        )

        self.assertIsNone(result["progress_percent"])
        self.assertEqual(result["expected_checks"], 0)


if __name__ == "__main__":
    unittest.main()
