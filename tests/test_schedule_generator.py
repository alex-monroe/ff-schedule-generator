import unittest
from unittest.mock import Mock, patch
from src import schedule_generator
import csv
import io

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
        
        expected_vars = []
        for team2 in self.teams:
            if team2 != 3:
                expected_vars.append(f'var_3_{team2}_5')
                expected_vars.append(f'var_{team2}_3_5')
        
        self.assertCountEqual(result, expected_vars)

        # Test with a team that doesn't exist
        result_invalid_team = schedule_generator.getTeamsVariablesForWeek(self.mock_variables, 99, 5, self.weeks, self.teams)
        self.assertEqual(result_invalid_team, [])

        # Test with a week that doesn't exist
        result_invalid_week = schedule_generator.getTeamsVariablesForWeek(self.mock_variables, 3, 99, self.weeks, self.teams)
        self.assertEqual(result_invalid_week, [])

    def test_getTeamsVariablesForAllWeeks(self):
        # Test for team 1 vs team 8
        result = schedule_generator.getTeamsVariablesForAllWeeks(self.mock_variables, 1, 8, self.weeks, self.teams)
        
        expected_vars = []
        for w in self.weeks:
            expected_vars.append(f'var_1_8_{w}')
            expected_vars.append(f'var_8_1_{w}')

        self.assertCountEqual(result, expected_vars)

        # Test with teams that don't exist
        result_invalid_teams = schedule_generator.getTeamsVariablesForAllWeeks(self.mock_variables, 99, 100, self.weeks, self.teams)
        self.assertEqual(result_invalid_teams, [])

    @patch('src.schedule_generator.pywraplp.Solver')
    def test_generate_schedule_csv_optimal_solution(self, MockSolver):
        mock_solver_instance = Mock()
        MockSolver.CreateSolver.return_value = mock_solver_instance

        # Mock solver behavior for optimal solution
        mock_solver_instance.Solve.return_value = schedule_generator.pywraplp.Solver.OPTIMAL
        mock_solver_instance.Objective.return_value.Value.return_value = 0
        
        # Mock variables with solution values
        mock_variables_solution = [[[Mock() for _ in range(2)] for _ in range(2)] for _ in range(2)]
        mock_variables_solution[0][1][0].solution_value.return_value = 1
        mock_variables_solution[1][0][0].solution_value.return_value = 1
        mock_variables_solution[0][1][1].solution_value.return_value = 1
        mock_variables_solution[1][0][1].solution_value.return_value = 1

        # Patch the internal _get_schedule_data to return a predictable schedule
        with patch('src.schedule_generator._get_schedule_data') as mock_get_schedule_data:
            mock_get_schedule_data.return_value = [
                ['Week', 'Team1', 'Team2'],
                [0, 0, 1],
                [0, 1, 0],
                [1, 0, 1],
                [1, 1, 0]
            ]
            result_csv = schedule_generator.generate_schedule_csv(2, 2) # 2 weeks, 2 teams

        expected_csv = "Week,Team1,Team2\r\n0,0,1\r\n0,1,0\r\n1,0,1\r\n1,1,0\r\n"
        self.assertEqual(result_csv, expected_csv)

    @patch('src.schedule_generator.pywraplp.Solver')
    def test_generate_schedule_csv_no_optimal_solution(self, MockSolver):
        mock_solver_instance = Mock()
        MockSolver.CreateSolver.return_value = mock_solver_instance

        # Mock solver behavior for no optimal solution
        mock_solver_instance.Solve.return_value = schedule_generator.pywraplp.Solver.INFEASIBLE

        result = schedule_generator.generate_schedule_csv(2, 2)
        self.assertEqual(result, "The problem does not have an optimal solution.")

    @patch('src.schedule_generator.pywraplp.Solver')
    def test_generate_schedule_csv_solver_creation_failure(self, MockSolver):
        MockSolver.CreateSolver.return_value = None

        result = schedule_generator.generate_schedule_csv(2, 2)
        self.assertEqual(result, "Error: Solver could not be created.")

if __name__ == '__main__':
    unittest.main()
