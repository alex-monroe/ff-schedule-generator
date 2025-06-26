import unittest
from unittest.mock import Mock
from src import schedule_generator

class TestScheduleGenerator(unittest.TestCase):

    def setUp(self):
        self.num_weeks = 13
        self.num_teams = 10
        self.weeks = range(self.num_weeks)
        self.teams = range(self.num_teams)
        # Create a mock 3D array of variables for testing
        self.mock_variables = [[[f'var_{i}_{j}_{w}' for w in self.weeks] for j in self.teams] for i in self.teams]

    def test_getTeamsVariablesForWeek(self):
        # Test for team 3, week 5
        result = schedule_generator.getTeamsVariablesForWeek(self.mock_variables, 3, 5, self.weeks, self.teams)
        
        # Team 3 should be playing one other team, so we expect two variables:
        # one for (team 3 vs opponent) and one for (opponent vs team 3)
        # However, the function gets all variables for the team in that week.
        expected_vars = []
        for team2 in self.teams:
            if team2 != 3:
                expected_vars.append(f'var_3_{team2}_5')
                expected_vars.append(f'var_{team2}_3_5')
        
        self.assertCountEqual(result, expected_vars)

    def test_getTeamsVariablesForAllWeeks(self):
        # Test for team 1 vs team 8
        result = schedule_generator.getTeamsVariablesForAllWeeks(self.mock_variables, 1, 8, self.weeks, self.teams)
        
        expected_vars = []
        for w in self.weeks:
            expected_vars.append(f'var_1_8_{w}')
            expected_vars.append(f'var_8_1_{w}')

        self.assertCountEqual(result, expected_vars)

if __name__ == '__main__':
    unittest.main()