let machine_id=null;
async function discoverMachine(){
    try{
        const response=await fetch("http://127.0.0.1:5001/identity")
        if(!response.ok) throw new Error("Couldnt FETCH MACHINE id ");
        const data= await response.json();
        machine_id=data.machine_id;
        console.log("HELIOS MACHINE ID :",machine_id);
        return true;
    }
    catch(error){
        connectionFailed();
        console.error(error);
        machine_id=null;
        return false;
    }
}

// Creating the Charts 
const ctx=document.getElementById("cpuChart").getContext("2d");
const cpuChart=new Chart(ctx,{
    type:"line",
    data:{
        labels:[],
        datasets:[{
            label:"CPU Usage",
            data:[]
        },{
            label:"Anomaly",
            data:[],
            backdropColor:"red",
            pointRadius:7,
            pointHoverRadius:10,
            showline:false
        }],
    },
    options:{
        responsive:true,
        plugins:{legend:{labels:{color:"#9baaff"}}},
        scales:{x:{ticks:{color:"#9baaff"}},y:{beginAtZero:true,max:100,ticks:{color:"#9baaff"}}}
    }
});
const centerText = {
    id: "centerText",
    beforeDraw(chart){
        const {ctx, width, height} = chart;
        ctx.save();
        ctx.font = "bold 30px Aldrich";
        ctx.fillStyle = "#9baaff";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        const value =
            chart.data.datasets[0].data[0];
        ctx.fillText(
            value + "%",
            width / 2,
            height / 2
        );
        ctx.restore();
    }
};
const dtx=document.getElementById("ramChart").getContext("2d");
const ramChart=new Chart(dtx,{
    type:"doughnut",
    data:{
        labels:["Used RAM","Available RAM"],
        datasets:[{
            data:[1,100],
            backgroundColor:["#8b17ff","#ffffff33"],
            borderWidth:0
        }]
    },
    options:{
        cutout:70,
        responsive:true,
        plugins:{legend:{labels:{color:"#9baaff"}}},
    },
    plugins:[centerText]
});

const ntx=document.getElementById("networkChart").getContext("2d");
const networkChart=new Chart(ntx,{
    type:"line",
    data:{
        labels:[],
        datasets:[{
            label:"Network TX (MB/s)",
            data:[],
            borderColor: "#e33ee65f",
            fill:true
        },{
            label:"Network RX (MB/s)",
            data:[],
            borderColor: "#8b17ff",
            fill:true
        },
        {
            label:"Anomaly",
            data:[],
            backdropColor:"red",
            pointRadius:7,
            pointHoverRadius:10,
            showline:false
        }
    ]},
    options:{
        responsive:true,
        plugins:{legend:{labels:{color:"#9baaff"}}},
        scales:{x:{ticks:{color:"#9baaff"},grid:{color:"#ffffff15"}},y:{beginAtZero:true,ticks:{color:"#9baaff"},grid:{color:"#ffffff15"}}}
    }
});

const optx=document.getElementById("overallPerformanceChart").getContext("2d")
const overallPerformanceChart=new Chart(optx,{
    type:"radar",
    data:{
        labels:["CPU Usage","RAM Usage","DISK","NETWORK"],
        datasets:[{
            label:"System Performance",
            data:[],
            pointBorderColor:["red","blue","green","orange"],
            pointBackgroundColor:["red","blue","green","orange"]
        }]
    },
    options:{
        responsive:true,
        plugins:{legend:{position:"top",labels:{color:"#9baaff"}}},
        scales:{r:{beginAtZero:true,max:100,pointLabels:{color:"#9baaff"},ticks:{color:"#9baaff",backdropColor:"transparent"},grid:{color:"#ffffff20"},angleLines:{color:"#ffffff20"}}}
    }
});

connectingStatus();
async function fetchTelemetry(){
    if(telemetryRunning){
        return;
    }
    if(!machine_id){
        return;
    }
    telemetryRunning = true;
    try{
        const response=await fetch(`https://helios-observability.onrender.com/api/metrics/live?machine_id=${encodeURIComponent(machine_id)}`)
        if(!response.ok) throw new Error("Couldnt FETCH Telemetry!");
        const data= await response.json();
        connectedStatus();
        updateUIElements(data.metric);
        updateCPUChart(data.metric,data.issues);
        updateRAM(data.metric,data.issues);
        updateNetwork(data.metric,data.issues);
        updateOverallPerformance(data.metric);
        updateAlert(data.anomaly,data.issues);
        updateSummary(data.summary);
    }
    catch(error){
        connectionFailed();
        console.error(error);
    }
    finally{
        telemetryRunning = false;
    }
}

async function fetchTelemetryAI(){
    if(!machine_id){
        return;
    }
    try{
        const response=await fetch(`/api/metrics/ai?machine_id=${encodeURIComponent(machine_id)}`)
        if(!response.ok) throw new Error("Couldnt FETCH error!");
        const data= await response.json();
        updateAiAnalysis(data.ai,data.status);
    }
    catch(error){
        connectionFailed();
        console.error(error);
    }
}

async function fetchTelemetryAnalysis(){
    if(!machine_id){
        return;
    }
    try{
        const response=await fetch(`/api/metrics/summary?machine_id=${encodeURIComponent(machine_id)}`)
        if(!response.ok) throw new Error("Couldnt FETCH error!");
        const data= await response.json();
        connectedStatus();
        updateUIsummary(data.summary);
    }
    catch(error){
        connectionFailed();
        console.error(error);
    }
}
function connectedStatus(){
    let status=document.getElementById("connection-status");
    status.innerHTML="🟢 Connected";
}

function connectingStatus(){
    let status=document.getElementById("connection-status");
    status.innerHTML="🟠 Connecting....";
}

function connectionFailed(){
    let status=document.getElementById("connection-status");
    status.innerHTML="🔴 Failed";
}

function updateUIElements(metric){
    //CPU Value
    let cpuValue=document.getElementById("cpu-reading");
    cpuValue.innerHTML=metric.cpu.cpu_usage+" %";

    //RAM Value
    let ramValue=document.getElementById("ram-reading");
    ramValue.innerHTML=metric.ram.percent+" %";

    //Disk Value
    let diskValue=document.getElementById("disk-reading");
    diskValue.innerHTML=metric.disk.disk_usage+" %";

    //Network Value
    let networkValue=document.getElementById("network-reading");
    networkValue.innerHTML=metric.network_activity.network_sent+" B";

}

function updateUIsummary(summary){
    let avgCpuValue=document.getElementById("avgCpu-reading");
    avgCpuValue.innerHTML=summary.average_cpu.toFixed(2);

    let maxRamValue=document.getElementById("maxRam-reading");
    maxRamValue.innerHTML=summary.maximum_ram;
}

function updateAlert(anomaly,issues){
   const alertBox=document.getElementById("alert-box");
   let issueHTML="";
    issues.forEach(issue=>{
        issueHTML+=`
        <h3>${issue.resource}</h3>
        <p>${issue.message}</P>
        `
    })
   if(anomaly===-1){
        anomalyDisplay = Date.now() + 10000;
        alertBox.classList.remove("alert-healthy");
        alertBox.classList.add("alert-anomaly");
        alertBox.innerHTML=`
        <div class="alert-anomaly">
            <h2>Anomaly Detected!</p>
            <p>${issueHTML}</>  
        </div> `;
   }
   if(Date.now() < anomalyDisplay){
        return;
    }
   else if(anomaly===0){
        alertBox.classList.add("alert-healthy");
        alertBox.classList.remove("alert-anomaly");
        alertBox.innerHTML= `
        <div class="alert-healthy">
            <h2>No Anomaly Found!</p>
        </div>`;
    }
}

function updateSummary(summary){
    const aiContainer=document.getElementById("summary-card");
    if(!summary){
        aiContainer.innerHTML="No AI Analysis available";
        return;
    }
    aiContainer.innerHTML=`
        <h2>${summary.status}</h2>
        <p>${summary.summary}</p>
    `;
}

function updateAiAnalysis(ai,status){
    const aiCard=document.getElementById("aiAnalysis");
    if(!ai) return;
    console.log("AI Status",ai);
    console.log("AI ",ai);
    aiCard.innerHTML=`
        <h3>Status:${status}</h3>
        <p>${ai.summary}</p><br>
        <p>${ai.root_cause}</p><br>
        <p>Likely Cause:</p>
        <ul>
            ${ai.contributors
                .map(process => `<li>${process}</li>`)
                .join("")}
        </ul>
        <p>Recommendations:</p>
        <ul>
            ${ai.recommendations
                .map(rec => `<li>${rec}</li>`)
                .join("")}
        </ul>
    `;

}

function updateCPUChart(metric,issues){
    const currentTime= new Date().toLocaleTimeString();
    cpuChart.data.labels.push(currentTime);
    cpuChart.data.datasets[0].data.push(metric.cpu.cpu_usage);
    const cpuIssue=issues.some(issue=>issue.resource==="CPU");
    if(cpuIssue){
        cpuChart.data.datasets[1].data.push(metric.cpu.cpu_usage); // it will turn to red colour;
    }
    else{
        cpuChart.data.datasets[1].data.push(null);
    }
    if(cpuChart.data.labels.length>4){
        cpuChart.data.labels.shift();
        cpuChart.data.datasets[0].data.shift();
        cpuChart.data.datasets[1].data.shift();
    }
    cpuChart.update();
}

function updateRAM(metric,issues){
    let used=metric.ram.percent;
    let free=100-metric.ram.percent;
    const ramIssue=issues.some(issue=>issue.resource==="RAM");
    console.log("ISSUES:", issues);
    console.log("RAM ISSUE:", ramIssue);
    if(ramIssue){
        ramChart.data.datasets[0].backgroundColor=["#da3c3997","#ffffff33"] ;// it will turn to red colour;
    }
    else{
        ramChart.data.datasets[0].backgroundColor=["#8b17ff","#ffffff33"] ;
    }
    ramChart.data.datasets[0].data=[used,free];
    ramChart.update();
}

function updateNetwork(metric,issues){
    const currentTime= new Date().toLocaleTimeString();
    networkChart.data.labels.push(currentTime);
    networkChart.data.datasets[0].data.push(metric.network_activity.network_sent);
    networkChart.data.datasets[1].data.push(metric.network_activity.network_received);
    const networkIssue=issues.some(issue=>issue.resource==="Network Sent & Network Received");
    if(networkIssue){
        const networkMax=Math.max(metric.network_activity.network_sent,metric.network_activity.network_received)
        networkChart.data.datasets[2].data.push(networkMax); 
        // it will turn to red colour;
    }
    else{
        networkChart.data.datasets[2].data.push(null);
    }
    if(networkChart.data.labels.length>4){
        networkChart.data.labels.shift();
        networkChart.data.datasets[0].data.shift();
        networkChart.data.datasets[1].data.shift();
        networkChart.data.datasets[2].data.shift();
    }
    networkChart.update();
}

function updateOverallPerformance(metric){
    let total=metric.network_activity.network_sent + metric.network_activity.network_received;
    let networkPercent=Math.min((total/100)*100,100);
    overallPerformanceChart.data.datasets[0].data=[metric.cpu.cpu_usage,metric.ram.percent,metric.disk.disk_usage,networkPercent];
    overallPerformanceChart.update();
}

let ingestionInterval=null;
let telemetryRunning = false;
let anomalyDisplay=0;
function systemMonitoring(){
    // if its not there set the timer once when its starts
    if(ingestionInterval===null) {
        ingestionInterval= setInterval(()=>{
            fetchTelemetry();
            fetchTelemetryAI();
        },2000)
    }
}

async function fetchTelemetryHistory(){
    if(!machine_id){
        return;
    }
    try{
        const now=Date.now()/1000;
        const start=now-(24*60*60);
        const end=now;
        const response=await fetch(`/api/metrics/history?machine_id=${encodeURIComponent(machine_id)}&start=${start}&end=${end}&page=1&limit=20`)
        if(!response.ok) throw new Error("Couldnt FETCH error!");
        const data= await response.json();
        updateTelmentryTable(data.history);
    }
    catch(error){
        connectionFailed();
        console.error(error);
    }
}

function updateTelmentryTable(history){
    const tableBody=document.getElementById("telmentry-table-body");
    tableBody.innerHTML="";
    history.forEach(record=>{
        const row=document.createElement("tr");
        const timeStamp=new Date(record.timeStamp * 1000).toLocaleTimeString();
        row.innerHTML= `
            <td>${timeStamp}</td>
            <td>${record.cpu_usage.toFixed(2)}%</td>
            <td>${record.disk_usage.toFixed(2)}%</td>
            <td>${record.ram_usage.toFixed(2)}</td>
            <td>${record.network_sent.toFixed(2)}</td>
            <td>${record.network_received.toFixed(2)}</td>
        `;
        tableBody.appendChild(row);
    })
}
async function startDashboard(){
    connectingStatus();
    const machineFound = await discoverMachine();
    if(!machineFound){
        connectionFailed();
        console.error(
            "HELIOS Agent is not running on this computer."
        );
        return;
    }
    console.log(
        "Starting dashboard for machine:",machine_id);
    fetchTelemetry();
    fetchTelemetryAI();
    fetchTelemetryAnalysis();
    fetchTelemetryHistory();
    systemMonitoring();
}

startDashboard();

window.addEventListener("beforeunload",()=>{
    clearInterval(ingestionInterval);
})
