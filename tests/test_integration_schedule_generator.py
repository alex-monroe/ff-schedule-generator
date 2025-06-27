import unittest
import logging
import schedule_generator

class TestScheduleGeneratorIntegration(unittest.TestCase):
    def test_generate_schedule_csv_real_solver(self):
        """Integration test using the real solver"""
        num_weeks = 13
        num_teams = 10

        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        )
        logging.info("Calling generate_schedule_csv with %d weeks and %d teams", num_weeks, num_teams)

        csv_output = schedule_generator.generate_schedule_csv(num_weeks, num_teams)

        logging.info("generate_schedule_csv returned %d characters of CSV", len(csv_output))

        self.assertNotEqual(csv_output, "The problem does not have an optimal solution.")
        self.assertNotEqual(csv_output, "Error: Solver could not be created.")

        lines = csv_output.strip().splitlines()
        self.assertEqual(lines[0], "Week,Team1,Team2")
        expected_lines = 1 + num_weeks * num_teams // 2
        self.assertEqual(len(lines), expected_lines)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    )
    unittest.main()
