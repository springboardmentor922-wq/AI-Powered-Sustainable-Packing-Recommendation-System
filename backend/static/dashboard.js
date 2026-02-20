let fullData = [];
let charts = {};

async function initDashboard(){
    const res = await fetch("/analytics-data");
    const data = await res.json();

    // Convert into unified structure
    fullData = data.eco_bar.labels.map((name,i)=>({
        name: name,
        biodeg: data.eco_bar.values[i],
        strength: data.strength_scatter.x[i],
        co2: data.strength_scatter.y[i]
    }));

    updateKPIs(fullData);
    drawAllCharts(fullData);
}

function updateKPIs(dataset){
    document.getElementById("total").innerText = dataset.length;
    document.getElementById("recycle").innerText =
        (dataset.reduce((a,b)=>a+b.biodeg,0)/dataset.length).toFixed(1)+"%";

    document.getElementById("co2").innerText =
        (dataset.reduce((a,b)=>a+b.co2,0)/dataset.length).toFixed(2);

    document.getElementById("cost").innerText =
        (dataset.reduce((a,b)=>a+(b.strength*0.3),0)/dataset.length).toFixed(2);
}

function drawAllCharts(dataset){
    destroyCharts();

    const names = dataset.map(d=>d.name);
    const strength = dataset.map(d=>d.strength);
    const biodeg = dataset.map(d=>d.biodeg);
    const co2 = dataset.map(d=>d.co2);

    charts.strengthChart = new Chart(strengthChart,{
        type:"line",
        data:{labels:names,datasets:[{data:strength,borderColor:"#16a34a",fill:false}]},
        options:{onClick:(e,i)=>filter(i,dataset)}
    });

    charts.bioChart = new Chart(bioChart,{
        type:"scatter",
        data:{datasets:[{data:biodeg.map((v,i)=>({x:i,y:v})),backgroundColor:"#22c55e"}]},
        options:{onClick:(e,i)=>filter(i,dataset)}
    });

    

    charts.bubbleChart = new Chart(bubbleChart,{
        type:"bubble",
        data:{datasets:[{data:strength.map((v,i)=>({x:v,y:co2[i],r:biodeg[i]/4})),backgroundColor:"#34d399"}]},
        options:{onClick:(e,i)=>filter(i,dataset)}
    });

    charts.effChart = new Chart(effChart,{
        type:"pie",
        data:{labels:names,datasets:[{data:biodeg,backgroundColor:["#16a34a","#22c55e","#4ade80","#15803d","#065f46","#14532d"]}]},
        options:{onClick:(e,i)=>filter(i,dataset)}
    });

    charts.radarChart = new Chart(radarChart,{
        type:"radar",
        data:{labels:names,datasets:[{data:co2,backgroundColor:"rgba(5,150,105,0.4)",borderColor:"#065f46"}]},
        options:{}
    });
    charts.sustainChart = new Chart(sustainChart,{
        type:"bar",
        data:{labels:names,datasets:[{data:biodeg,backgroundColor:"#10b981"}]},
        options:{onClick:(e,i)=>filter(i,dataset)}
    });
}

function filter(items,dataset){
    if(items.length===0) return;
    const index = items[0].index;
    const selected = dataset[index];
    drawAllCharts([selected]);
    updateKPIs([selected]);
}

function destroyCharts(){
    Object.values(charts).forEach(c=>c.destroy());
    charts = {};
}

window.onload = initDashboard;