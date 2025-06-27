import unittest
import logging
import schedule_generator


class TestScheduleGeneratorIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run the real solver once for all tests in this class."""
        cls.num_weeks = 13
        cls.num_teams = 10

        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        )
        logging.info(
            "Calling generate_schedule with %d weeks and %d teams",
            cls.num_weeks,
            cls.num_teams,
        )

        cls.schedule_data = schedule_generator.generate_schedule(
            cls.num_weeks, cls.num_teams
        )

        logging.info(
            "generate_schedule returned %d rows", len(cls.schedule_data)
        )

    def test_generate_schedule_real_solver(self):
        """Basic sanity checks on the solver output."""

        self.assertNotEqual(
            self.schedule_data,
            "The problem does not have an optimal solution.",
        )
        self.assertNotEqual(
            self.schedule_data,
            "Error: Solver could not be created.",
        )

        self.assertEqual(self.schedule_data[0], ["Week", "Team1", "Team2"])
        expected_rows = 1 + self.num_weeks * self.num_teams // 2
        self.assertEqual(len(self.schedule_data), expected_rows)

    def test_no_team_plays_itself(self):
        """Ensure no matchup contains the same team twice."""
        for _, team1, team2 in self.schedule_data[1:]:
            self.assertNotEqual(team1, team2)

    def test_team_plays_once_per_week(self):
        """Ensure each team appears only once per week."""
        weeks = {week: [] for week in range(self.num_weeks)}
        for week, team1, team2 in self.schedule_data[1:]:
            weeks[week].extend([team1, team2])

        for week, teams in weeks.items():
            with self.subTest(week=week):
                self.assertEqual(len(teams), self.num_teams)
                self.assertEqual(len(set(teams)), self.num_teams)

    def test_no_repeated_matchups_within_four_weeks(self):
        """Ensure teams do not repeat a matchup within a 4 week span."""
        pair_weeks = {}
        for week, team1, team2 in self.schedule_data[1:]:
            pair = tuple(sorted((team1, team2)))
            pair_weeks.setdefault(pair, []).append(week)

        for pair, weeks in pair_weeks.items():
            weeks.sort()
            for i in range(len(weeks) - 1):
                diff = weeks[i + 1] - weeks[i]
                self.assertGreaterEqual(
                    diff,
                    4,
                    msg=f"Pair {pair} repeats within {diff} weeks",
                )


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    )
    unittest.main()
