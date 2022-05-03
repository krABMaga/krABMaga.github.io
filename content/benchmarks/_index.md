+++
title = "Benchmarks"
insert_anchor_links = "right"
+++

---

<link rel="stylesheet" href="/benchmarks/benchmarks.css">


# ABM Benchmark
<!-- 
color code main index
 -->

All the benchmarks have been executed on the same machine with the same configurations. 
We started from a 100x100 field with 1000 agents and then we doubled the number of agents for each configuration, calculating the field with the same density.
ForestFire is the only example where there isn't a clear number of agents, but there is a parameter of the simulation for the density (to clarify, it is 70%). 
You can see all the script and files used for benchmark all the engines at the [ABM_comparison](https://github.com/rust-ab/abmcomparison).

We compared our results with the most commons frameworks for ABM:
- [MASON](https://cs.gmu.edu/~eclab/projects/mason/) is a fast discrete-event multiagent simulation library core written in Java
- [Agents.jl](https://juliadynamics.github.io/Agents.jl/stable/) is a pure Julia framework for agent-based modeling
- [Repast](https://repast.github.io/) is a tightly integrated, richly interactive, cross platform Java-based modeling system
- [Netlogo](https://ccl.northwestern.edu/netlogo/) is a multi-agent programmable modeling environment
- [Mesa](https://mesa.readthedocs.io/en/latest/#) is an agent-based modeling framework written in Python.

There are two types of charts:

- Time: this chart plots the average time of simulations
- Speedup: this charts plots the speed up of krABMaga versus the others engines.

You can choose one of the model using the radio buttons on the bottom of the chart and you can also choose which type of chart to display using the combobox.
You can click on the various engine on the top legend to show or hide their corresponding values on the chart.
    
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
<div>
  <canvas id="myChart" width="400" height="150" style="background-color: white;"></canvas>
</div>
<div class="button-group" data-toggle="buttons" id="charts">
    <div class="button">
        <input type="radio" name="options" id="flockers" autocomplete="off" checked /> 
        <label class="btn btn-default" for="flockers">Flockers
        </label>
    </div>
    <div class="button">
        <input type="radio" name="options" id="forestfire" autocomplete="off" /> 
        <label class="btn btn-default" for="forestfire"> ForestFire
        </label>
    </div>
    <div class="button">
        <input type="radio" name="options" id="schelling" autocomplete="off" /> 
        <label class="btn btn-default" for="schelling"> Schelling
        </label>
    </div>
    <div class="button">
        <input type="radio" name="options" id="wsg" autocomplete="off" /> 
        <label class="btn btn-default" for="wsg"> Wsg
        </label>
    </div>
</div>
<select class="combotype select-css" value="time" id="combocharts">
    <option value="time" id="timecombo" selected>Time</option>
    <option value="speedup" id="speedupcombo">Speedup</option>
</select>


<script>
var myChart;
var real_data = [];
var real_names = [];
function drawAsync(chartName){
    return new Promise((resolve,reject)=>{
        //clear the array on each draw 
        real_data = [];
        real_names = [];
        fetch("../csv/" + chartName + ".csv").then((result)=>{result.text().then((text)=>{
            var a = text.split(/\r\n|\n/);
            for (var i=2; i<a.length; i++){
                var name = a[i].split(",")[0];
                real_names.push(name);
                //split the string by comma
                formatted = a[i].replace(/,/g, '.');
                //retrieve the decimal numbers from a[i] using regex
                var numbers = formatted.match(/\d+\.\d+/g);
                //convert the array of strings to an array of numbers
                numbers = numbers.map(Number);
                //create a new array from numbers taking every third elements (eliminate useless information like init ant step)
                numbers2 = numbers.filter((x,i)=>i%3==2);
                // create an array of pairs (x, y) from each element of numbers2 and a number that start from 1000 and multiply it by 2 at pow of i with 
                // the result being the x coordinate of the point
                dataset_pair = numbers2.map((x,i)=>[x,1000*Math.pow(2,i)]);
                // create a struct
                var my_data = [];
                for (j=0; j<dataset_pair.length; j++) {
                    my_data.push({x: dataset_pair[j][1], y: dataset_pair[j][0]});
                }
                real_data.push(my_data); 
            }
        })});
        setTimeout(()=>{
            resolve();
        ;} , 1000
        );
    });
}
async function draw(chartName){
    await drawAsync(chartName);
    const labels = [
        'Test',
    ];

    var details = [
        {
            name: "Rust-AB",
            col: 'rgba(255, 99, 132, 0.9)',
            mrk: 'circle',
        },
        {
            name: "MASON",
            col: 'rgba(54, 162, 235, 0.9)',
            mrk: 'cross',
        },
        {
            name: "Agent.jl",
            col: 'rgba(255, 206, 86, 0.9)',
            mrk: 'crossRot',
        },
        {
            name: "Repast",
            col: 'rgba(75, 192, 192, 0.9)',
            mrk: 'rectRot',
        },
        {
            name: "Netlogo",
            col: 'rgba(153, 102, 255, 0.9)',
            mrk: 'star',
        },
        {
            name: "Mesa",
            col: 'rgba(255, 159, 64, 0.9)',
            mrk: 'triangle',
        },
    ];

    const datasets = real_data.map((x,i)=>{
        return {
            label: real_names[i],
            data: x,
            backgroundColor: details.filter((x)=>x.name==real_names[i]).map(x=>x.col),
            borderColor: details.filter((x)=>x.name==real_names[i]).map(x=>x.col),
            borderWidth: 1,
            fill: false,
            pointStyle: details.filter((x)=>x.name==real_names[i]).map(x=>x.mrk),
            radius: 5,
        }
    });
    const data = {
        labels: labels,
        datasets: datasets,
    };

    var title_y = "seconds";
    if (document.getElementById("combocharts").value == "speedup"){
        title_y = "speedup";
    }

    const config = {
        type: 'scatter',
        data: data,
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'logarithmic',
                    position: 'bottom',
                    min: 950,
                    max: 130000,
                    title: {
                        text: '# of agents',
                        display: true,
                    }
                },
                y: {
                    type: 'logarithmic',
                    min: 0,
                    max: 100000,
                    drawTicks: false,
                    title: {
                        text: title_y,
                        display: true,
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: chartName
                },
            },       
        },
    };
    myChart = new Chart(
    document.getElementById('myChart'),
    config,
  );
}
// name of the file csv to retrieve data
// this function is called on page load for the first time
// use the buttons to change the csv loaded
draw("flockers");
//check on radio
document.getElementById("charts").addEventListener('click', function (event) {
    if (event.target && event.target.matches("input[type='radio']")) {
        if (document.getElementById("combocharts").value == "time") {
            myChart.destroy();
            draw(event.target.id);
            myChart.update();
        }
        else {
            myChart.destroy();
            draw(event.target.id + "speedup");
            myChart.update();
        }
        
}});
//check on select option
document.getElementById("combocharts").addEventListener('change', function (event) {
    if (event.target && event.target.matches("select")) {
        if (event.target.value == "time") {
            var id = document.querySelector('input[name="options"]:checked').id;
            myChart.destroy();
            draw(id);
            myChart.update();
        }
        else {
            var id = document.querySelector('input[name="options"]:checked').id;
            myChart.destroy();
            draw(id + "speedup");
            myChart.update();
        }
    }
});
</script>