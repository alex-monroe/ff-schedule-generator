document.addEventListener('DOMContentLoaded', () => {
    const teamsList = document.getElementById('teams-list');
    const teamNameInput = document.getElementById('team-name');
    const teamDivisionSelect = document.getElementById('team-division');
    const addTeamButton = document.getElementById('add-team');

    const divisionsList = document.getElementById('divisions-list');
    const divisionNameInput = document.getElementById('division-name');
    const addDivisionButton = document.getElementById('add-division');

    const generateScheduleButton = document.getElementById('generate-schedule');
    const scheduleOutput = document.getElementById('schedule-output');

    let teams = [];
    let divisions = [];
    let divisionIdCounter = 1;

    addDivisionButton.addEventListener('click', () => {
        const divisionName = divisionNameInput.value.trim();
        if (divisionName) {
            const newDivision = { name: divisionName, id: divisionIdCounter++ };
            divisions.push(newDivision);
            renderDivisions();
            divisionNameInput.value = '';
        }
    });

    addTeamButton.addEventListener('click', () => {
        const teamName = teamNameInput.value.trim();
        const divisionId = parseInt(teamDivisionSelect.value, 10);
        if (teamName && !isNaN(divisionId)) {
            teams.push({ name: teamName, division_id: divisionId });
            renderTeams();
            teamNameInput.value = '';
        }
    });

    generateScheduleButton.addEventListener('click', async () => {
        const requestBody = {
            league: teams,
            divisions: divisions
        };

        try {
            const response = await fetch('/generate-schedule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            if (response.ok) {
                const data = await response.json();
                renderSchedule(data);
            } else {
                const error = await response.json();
                scheduleOutput.textContent = `Error: ${error.error}`;
            }
        } catch (error) {
            scheduleOutput.textContent = `Error: ${error.message}`;
        }
    });

    function renderDivisions() {
        divisionsList.innerHTML = '';
        teamDivisionSelect.innerHTML = '';
        divisions.forEach(division => {
            const divisionElement = document.createElement('div');
            divisionElement.textContent = `${division.name} (ID: ${division.id})`;
            divisionsList.appendChild(divisionElement);

            const optionElement = document.createElement('option');
            optionElement.value = division.id;
            optionElement.textContent = division.name;
            teamDivisionSelect.appendChild(optionElement);
        });
    }

    function renderTeams() {
        teamsList.innerHTML = '';
        teams.forEach(team => {
            const teamElement = document.createElement('div');
            const division = divisions.find(d => d.id === team.division_id);
            teamElement.textContent = `${team.name} (Division: ${division.name})`;
            teamsList.appendChild(teamElement);
        });
    }

    function renderSchedule(data) {
        scheduleOutput.innerHTML = '';
        if (data.matchups) {
            data.matchups.forEach((weeklyMatchup, index) => {
                const weekElement = document.createElement('div');
                weekElement.innerHTML = `<h3>Week ${index + 1}</h3>`;
                const matchupsList = document.createElement('ul');
                if (weeklyMatchup.matchups) {
                    weeklyMatchup.matchups.forEach(matchup => {
                        const matchupItem = document.createElement('li');
                        matchupItem.textContent = `${matchup.team1.name} vs ${matchup.team2.name}`;
                        matchupsList.appendChild(matchupItem);
                    });
                }
                weekElement.appendChild(matchupsList);
                scheduleOutput.appendChild(weekElement);
            });
        } else {
            scheduleOutput.innerHTML = '<p>No schedule generated.</p>';
        }
    }
});
