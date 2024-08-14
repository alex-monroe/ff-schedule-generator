from ortools.linear_solver import pywraplp
import csv

weeks = range(13)
teams = range(10)

# Generates a 13 week schedule for a 10 team league.
# Assumes 2 divisions, where each team plays teams in its own division twice and each team outside its division once.
def main():
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SAT")
    if not solver:
        return

    infinity = solver.infinity()

    # Each variable x[i][j][w] is a decision variable such that:
    #    if x[i][j][w] == 1, then team i plays team j in week w
    #    if x[i][j][w] == 0, then team i does not play team j in week w
    variables = [[[0 for k in weeks] for j in teams] for i in teams]
    for j in range(10):
      for k in range(10):
          for w in range(13):
              variables[j][k][w] = solver.IntVar(0, infinity, f"x[{j}][{k}][{w}]")
    
    print("Number of variables =", solver.NumVariables())

    # no team plays itself
    # x[i][i][w] = 0 for each week w, for each team i
    for week in weeks:
        for team in teams:
            constraint = solver.RowConstraint(0, 0, "")
            constraint.SetCoefficient(variables[team][team][week], 1)

    # each team plays 1 game per week
    #   for each week and each team
    #      sum of all variables inlucding that team for that week = 2
    for week in weeks:
        for team in teams:
            constraint = solver.RowConstraint(2, 2, "")
            for variable in getTeamsVariablesForWeek(variables, team, week):
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
    
    # Teams within the division play each other twice
    # for each team combination in each division, for all weeks
    #  sum( x[i][j][w] ) = 4 
    for team in teams:
        for team2 in teams:
            if (team != team2) and ((team < 5 and team2 < 5) or (team > 4 and team2 > 4)):
                constraint = solver.RowConstraint(4, 4, "")
                for variable in getTeamsVariablesForAllWeeks(variables, team, team2):
                    constraint.SetCoefficient(variable, 1)

    # Teams play out of division opponents once
    # for each team combination outside each division, for all weeks
    #  sum( x[i][j][w] ) = 2 
    for team in teams:
        for team2 in teams:
            if (team != team2) and not ((team < 5 and team2 < 5) or (team > 4 and team2 > 4)):
                constraint = solver.RowConstraint(2, 2, "")
                for variable in getTeamsVariablesForAllWeeks(variables, team, team2):
                    constraint.SetCoefficient(variable, 1)

    # Teams do not play the same matchup in the same 4 week span
    for team in teams:
        for team2 in teams:
            for week in weeks[:-3]:
                if team > team2:
                    constraint = solver.RowConstraint(0, 1, "")
                    constraint.SetCoefficient(variables[team][team2][week], 1)
                    constraint.SetCoefficient(variables[team][team2][week+1], 1)
                    constraint.SetCoefficient(variables[team][team2][week+2], 1)
                    constraint.SetCoefficient(variables[team][team2][week+3], 1)

    # Try your best to not schedule out of division games for the last 2 weeks
    # (to avoid potential rematches in week 14)
    objective = solver.Objective()
    for team in teams:
        for team2 in teams:
            if (team != team2) and ((team < 5 and team2 < 5) or (team > 4 and team2 > 4)):
                objective.SetCoefficient(variables[team][team2][-1], 1)
                objective.SetCoefficient(variables[team][team2][-2], 1)
    objective.SetMaximization()


    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print("Solution:")
        print("Objective value =", solver.Objective().Value())
        printSchedule(variables)     
    else:
        print("The problem does not have an optimal solution.")

    print("\nAdvanced usage:")
    print(f"Problem solved in {solver.wall_time():d} milliseconds")
    print(f"Problem solved in {solver.iterations():d} iterations")
    print(f"Problem solved in {solver.nodes():d} branch-and-bound nodes")


# Returns all of the variables in variables that correspond to the given team playing in a game in the given week
# Excludes variables representing the team playing itself
def getTeamsVariablesForWeek(variables, team, week):
    teamsVariables = []
    for w in weeks:
        for i in teams:
            for j in teams: 
                if ((i == team) or (j == team)) and (i != j) and (w == week):
                    teamsVariables.append(variables[i][j][w])
    return teamsVariables

# Returns all of the variables in variables that represent team 1 playing in team 2 in any week
def getTeamsVariablesForAllWeeks(variables, team1, team2):
    teamsVariables = []
    for w in weeks:
        for i in teams:
            for j in teams: 
                if ((i == team1) and (j == team2)) or ((i == team2) and (j == team1)):
                    teamsVariables.append(variables[i][j][w])
    return teamsVariables


def printSchedule(variables):
    with open('schedule.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Instead of print(), use writer.writerow()
        writer.writerow(['Week', 'Team1', 'Team2'])
        for w in weeks: 
            for i in teams:
                for j in teams:
                  if (variables[i][j][w].solution_value() > 0) :
                      writer.writerow([w, i, j]) 


if __name__ == "__main__":
    main()