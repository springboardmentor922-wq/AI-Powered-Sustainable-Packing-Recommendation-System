async function loadDashboard() {
    const response = await fetch("http://127.0.0.1:5000/recommend", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            distance: 500,
            packaging_type: "Electronics"
        })
    });

    const data = await response.json();

    if (data.status !== "success") {
        alert("Failed to load dashboard data");
        return;
    }

    const materials = data.recommendations;

    const labels = materials.map(m => m.material_name);
    const scores = materials.map(m => m.Final_Ranking_Score);

    new Chart(document.getElementById("materialChart"), {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Sustainability Score",
                data: scores,
                backgroundColor: "rgba(0, 255, 150, 0.6)"
            }]
        },
        options: {
            plugins: {
                legend: { labels: { color: "white" } }
            },
            scales: {
                x: { ticks: { color: "white" } },
                y: { ticks: { color: "white" } }
            }
        }
    });

    new Chart(document.getElementById("co2Chart"), {
        type: "doughnut",
        data: {
            labels: ["CO₂ Efficiency"],
            datasets: [{
                data: [75, 25],
                backgroundColor: ["#00ffcc", "#444"]
            }]
        }
    });

    new Chart(document.getElementById("costChart"), {
        type: "doughnut",
        data: {
            labels: ["Cost Efficiency"],
            datasets: [{
                data: [70, 30],
                backgroundColor: ["#ffcc00", "#444"]
            }]
        }
    });
}

loadDashboard();
