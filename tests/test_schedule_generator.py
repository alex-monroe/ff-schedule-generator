import unittest
from unittest.mock import Mock
from src import schedule_generator

class TestScheduleGenerator(unittest.TestCase):

    def setUp(self):
        # Create a mock 3D array of variables for testing
        self.mock_variables = [[[f'var_{i}_{j}_{w}' for w in range(13)] for j in range(10)] for i in range(10)]
        schedule_generator.weeks = range(13)
        schedule_generator.teams = range(10)

    def test_getTeamsVariablesForWeek(self):
        # Test for team 3, week 5
        result = schedule_generator.getTeamsVariablesForWeek(self.mock_variables, 3, 5)
        
        # Team 3 should be playing one other team, so we expect two variables:
        # one for (team 3 vs opponent) and one for (opponent vs team 3)
        # However, the function gets all variables for the team in that week.
        expected_vars = []
        for team2 in range(10):
            if team2 != 3:
                expected_vars.append(f'var_3_{team2}_5')
                expected_vars.append(f'var_{team2}_3_5')
        
        self.assertCountEqual(result, expected_vars)

    def test_getTeamsVariablesForAllWeeks(self):
        # Test for team 1 vs team 8
        result = schedule_generator.getTeamsVariablesForAllWeeks(self.mock_variables, 1, 8)
        
        expected_vars = []
        for w in range(13):
            expected_vars.append(f'var_1_8_{w}')
            expected_vars.append(f'var_8_1_{w}')

        self.assertCountEqual(result, expected_vars)

if __name__ == '__main__':
    unittest.main()
