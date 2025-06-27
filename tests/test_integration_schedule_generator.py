import unittest
import logging
import schedule_generator

class TestScheduleGeneratorIntegration(unittest.TestCase):
    def test_generate_schedule_real_solver(self):
        """Integration test using the real solver"""
        num_weeks = 13
        num_teams = 10

        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        )
        logging.info("Calling generate_schedule with %d weeks and %d teams", num_weeks, num_teams)

        schedule_data = schedule_generator.generate_schedule(num_weeks, num_teams)

        logging.info("generate_schedule returned %d rows", len(schedule_data))

        self.assertNotEqual(schedule_data, "The problem does not have an optimal solution.")
        self.assertNotEqual(schedule_data, "Error: Solver could not be created.")

        self.assertEqual(schedule_data[0], ["Week", "Team1", "Team2"])
        expected_rows = 1 + num_weeks * num_teams // 2
        self.assertEqual(len(schedule_data), expected_rows)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    )
    unittest.main()
