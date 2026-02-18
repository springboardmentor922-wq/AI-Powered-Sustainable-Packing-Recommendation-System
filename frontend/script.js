async function getRecommendation() {

    const distance = Number(document.getElementById("distance").value);
    const packaging = document.getElementById("packaging").value;
    const category = document.getElementById("category").value;
    const weight = Number(document.getElementById("weight").value);
    const volumetricWeight = Number(document.getElementById("volumetric_weight").value);
    const fragility = Number(document.getElementById("fragility").value);
    const moisture = Number(document.getElementById("moisture").value);
    const shippingMode = document.getElementById("shipping_mode").value;

    const response = await fetch("http://127.0.0.1:5000/recommend", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            distance: distance,
            packaging_type: packaging,
            category: category,
            weight: weight,
            volumetric_weight: volumetricWeight,
            fragility: fragility,
            moisture: moisture,
            shipping_mode: shippingMode
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
                    <td>${item.Adjusted_Cost.toFixed(3)}</td>
                    <td>${item.Adjusted_CO2.toFixed(3)}</td>
                </tr>
            `;
            table.innerHTML += row;
        });

    } else {
        alert(data.message);
    }
}
