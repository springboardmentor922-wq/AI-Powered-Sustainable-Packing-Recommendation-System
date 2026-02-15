async function getRecommendation() {
    const distance = document.getElementById("distance").value;
    const packaging = document.getElementById("packaging").value;

    const response = await fetch("http://127.0.0.1:5000/recommend", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            distance: Number(distance),
            packaging_type: packaging
        })
    });

    const data = await response.json();

    const table = document.getElementById("resultTable");
    table.innerHTML = "";

    if (data.status === "success") {
        data.recommendations.forEach(item => {
            const row = `
                <tr>
                    <td>${item.material_name}</td>
                    <td>${item.Final_Ranking_Score.toFixed(3)}</td>
                </tr>
            `;
            table.innerHTML += row;
        });
    } else {
        alert(data.message);
    }
}
