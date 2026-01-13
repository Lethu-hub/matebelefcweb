// stats/static/stats/js/analytics.js

let playerChart, teamChart;

// Helper: build table
function buildTable(tableId, data) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    tbody.innerHTML = "";
    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.player}</td>
            <td>${row.match_date}</td>
            <td>${row.event_type}</td>
            <td>${row.minute}</td>
            <td>${row.season}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Helper: build chart
function buildChart(canvasId, type, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (canvasId === 'player-chart' && playerChart) playerChart.destroy();
    if (canvasId === 'team-chart' && teamChart) teamChart.destroy();

    const labels = data.map(d => d.player);
    const values = data.map(d => d.minute);

    const chartConfig = {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: 'Event Minute',
                data: values,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        }
    };

    if (canvasId === 'player-chart') playerChart = new Chart(ctx, chartConfig);
    if (canvasId === 'team-chart') teamChart = new Chart(ctx, chartConfig);
}

// Player analytics
function loadPlayerAnalytics() {
    const players = Array.from(document.getElementById("player-player").selectedOptions).map(o => o.value);
    const matches = Array.from(document.getElementById("player-match").selectedOptions).map(o => o.value);
    const seasons = Array.from(document.getElementById("player-season").selectedOptions).map(o => o.value);
    const events = Array.from(document.getElementById("player-event").selectedOptions).map(o => o.value);

    fetch(`/stats/data?players[]=${players.join("&players[]=")}&matches[]=${matches.join("&matches[]=")}&seasons[]=${seasons.join("&seasons[]=")}&event_types[]=${events.join("&event_types[]=")}`)
        .then(res => res.json())
        .then(data => {
            buildTable("player-table", data);
            const chartType = document.getElementById("player-chart-type").value;
            buildChart("player-chart", chartType, data);
        });
}

// Team analytics
function loadTeamAnalytics() {
    const players = Array.from(document.getElementById("team-player").selectedOptions).map(o => o.value);
    const matches = Array.from(document.getElementById("team-match").selectedOptions).map(o => o.value);
    const seasons = Array.from(document.getElementById("team-season").selectedOptions).map(o => o.value);
    const events = Array.from(document.getElementById("team-event").selectedOptions).map(o => o.value);

    fetch(`/stats/data?players[]=${players.join("&players[]=")}&matches[]=${matches.join("&matches[]=")}&seasons[]=${seasons.join("&seasons[]=")}&event_types[]=${events.join("&event_types[]=")}`)
        .then(res => res.json())
        .then(data => {
            buildTable("team-table", data);
            const chartType = document.getElementById("team-chart-type").value;
            buildChart("team-chart", chartType, data);
        });
}

// Team auto-select players based on match
function updateTeamPlayers() {
    const selectedMatches = Array.from(document.getElementById("team-match").selectedOptions).map(o => o.value);
    fetch(`/stats/data?matches[]=${selectedMatches.join("&matches[]=")}`)
        .then(res => res.json())
        .then(data => {
            const uniquePlayers = [...new Set(data.map(d => d.player_id))];
            const teamPlayerSelect = document.getElementById("team-player");
            teamPlayerSelect.innerHTML = "";
            uniquePlayers.forEach(id => {
                const playerName = data.find(d => d.player_id === id).player;
                const option = document.createElement("option");
                option.value = id;
                option.text = playerName;
                option.selected = true;
                teamPlayerSelect.appendChild(option);
            });
        });
}
