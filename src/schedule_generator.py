import logging
from ortools.linear_solver import pywraplp

logger = logging.getLogger(__name__)


# Returns all of the variables in variables that correspond to the
# given team playing in a game in the given week
# Excludes variables representing the team playing itself
def getTeamsVariablesForWeek(variables, team, week, weeks_param, teams_param):
    teamsVariables = []
    for w in weeks_param:
        for i in teams_param:
            for j in teams_param:
                if ((i == team) or (j == team)) and (i != j) and (w == week):
                    teamsVariables.append(variables[i][j][w])
    return teamsVariables


# Returns all of the variables in variables that represent team 1 playing in team 2 in any week
def getTeamsVariablesForAllWeeks(variables, team1, team2, weeks_param, teams_param):
    teamsVariables = []
    for w in weeks_param:
        for i in teams_param:
            for j in teams_param:
                if ((i == team1) and (j == team2)) or ((i == team2) and (j == team1)):
                    teamsVariables.append(variables[i][j][w])
    return teamsVariables


def _get_schedule_data(variables, weeks_param, teams_param):
    schedule_data = []
    schedule_data.append(["Week", "Team1", "Team2"])
    for w in weeks_param:
        for i in teams_param:
            for j in teams_param:
                # each matchup is represented twice in the solver (i vs j and
                # j vs i).  Only record one of them in the schedule output.
                if (i < j) and (variables[i][j][w].solution_value() > 0):
                    schedule_data.append([w, i, j])
    return schedule_data


def generate_schedule(
    num_weeks,
    num_teams,
    in_division_play_twice=False,
    out_of_division_play_once=False,
):
    logger.info(
        "Generating schedule: %d weeks, %d teams", num_weeks, num_teams
    )
    weeks = range(num_weeks)
    teams = range(num_teams)

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SAT")
    if not solver:
        logger.error("Solver could not be created")
        return "Error: Solver could not be created."

    infinity = solver.infinity()

    # Each variable x[i][j][w] is a decision variable such that:
    #    if x[i][j][w] == 1, then team i plays team j in week w
    #    if x[i][j][w] == 0, then team i does not play team j in week w
    variables = [[[0 for k in weeks] for j in teams] for i in teams]
    for j in range(num_teams):
        for k in range(num_teams):
            for w in range(num_weeks):
                variables[j][k][w] = solver.IntVar(0, infinity, f"x[{j}][{k}][{w}]")

    # no team plays itself
    # x[i][i][w] = 0 for each week w, for each team i
    for week in weeks:
        for team in teams:
            constraint = solver.RowConstraint(0, 0, "")
            constraint.SetCoefficient(variables[team][team][week], 1)

    # each team plays 1 game per week
    #   for each week and each team
    #      sum of all variables including that team for that week = 2
    for week in weeks:
        for team in teams:
            constraint = solver.RowConstraint(2, 2, "")
            for variable in getTeamsVariablesForWeek(variables, team, week, weeks, teams):
                constraint.SetCoefficient(variable, 1)

    # when team 1 plays team 2 in a given week, ensure team 2 plays team 1
    # for each team combination, for each week, x[i][j][w] - x[j][i][w] = 0
    for team in teams:
        for team2 in teams:
            if team > team2:
                for week in weeks:
                    constraint = solver.RowConstraint(0, 0, "")
                    constraint.SetCoefficient(variables[team][team2][week], 1)
                    constraint.SetCoefficient(variables[team2][team][week], -1)

    if in_division_play_twice:
        # Teams within the division play each other twice
        # for each team combination in each division, for all weeks
        #  sum( x[i][j][w] ) = 4
        for team in teams:
            for team2 in teams:
                if (team != team2) and (
                    (team < num_teams / 2 and team2 < num_teams / 2)
                    or (team >= num_teams / 2 and team2 >= num_teams / 2)
                ):
                    constraint = solver.RowConstraint(4, 4, "")
                    for variable in getTeamsVariablesForAllWeeks(
                        variables, team, team2, weeks, teams
                    ):
                        constraint.SetCoefficient(variable, 1)

    if out_of_division_play_once:
        # Teams play out of division opponents once
        # for each team combination outside each division, for all weeks
        #  sum( x[i][j][w] ) = 2
        for team in teams:
            for team2 in teams:
                if (team != team2) and not (
                    (team < num_teams / 2 and team2 < num_teams / 2)
                    or (team >= num_teams / 2 and team2 >= num_teams / 2)
                ):
                    constraint = solver.RowConstraint(2, 2, "")
                    for variable in getTeamsVariablesForAllWeeks(
                        variables, team, team2, weeks, teams
                    ):
                        constraint.SetCoefficient(variable, 1)

    # Teams do not play the same matchup in the same 4 week span
    for team in teams:
        for team2 in teams:
            for week in weeks[:-3]:
                if team > team2:
                    constraint = solver.RowConstraint(0, 1, "")
                    constraint.SetCoefficient(variables[team][team2][week], 1)
                    constraint.SetCoefficient(variables[team][team2][week + 1], 1)
                    constraint.SetCoefficient(variables[team][team2][week + 2], 1)
                    constraint.SetCoefficient(variables[team][team2][week + 3], 1)

    # Try your best to not schedule out of division games for the last 2 weeks
    # (to avoid potential rematches in week 14)
    objective = solver.Objective()
    for team in teams:
        for team2 in teams:
            if (team != team2) and (
                (team < num_teams / 2 and team2 < num_teams / 2)
                or (team >= num_teams / 2 and team2 >= num_teams / 2)
            ):
                objective.SetCoefficient(variables[team][team2][-1], 1)
                objective.SetCoefficient(variables[team][team2][-2], 1)
    objective.SetMaximization()

    status = solver.Solve()
    logger.info("Solver finished with status %s", status)

    if status == pywraplp.Solver.OPTIMAL:
        schedule_data = _get_schedule_data(variables, weeks, teams)
        logger.info("Generated schedule with %d matchups", len(schedule_data) - 1)
        return schedule_data
    else:
        logger.error("The problem does not have an optimal solution.")
        return "The problem does not have an optimal solution."


def main():
    # Default values for weeks and teams
    default_weeks = 13
    default_teams = 10
    schedule_data = generate_schedule(default_weeks, default_teams)
    print(schedule_data)


if __name__ == "__main__":
    main()
