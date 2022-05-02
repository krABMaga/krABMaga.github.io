+++
title = "Charts"
insert_anchor_links = "right"
+++

---

<link rel="stylesheet" href="/charts/charts.css">


# ABM Benchmark
<!-- 
color code main index
 -->

## Usage

There are two types of charts:

    - Time: chart plots the average time of simulations
    - Speedup: charts plots the speed up of krABMaga versus the others engines.

You can choose one of the model using the radio buttons on the bottom of the chart and you can also choose which type of chart to display using the combobox.
You can click on the various engine on the top legend to show or hide their corresponding values on the chart.
<style>
    .button {
  display: table-cell;
  float: left;
  padding: 20px 0 0 0;
  vertical-align: middle;
  margin: 0 0 0 0;
  width: 100px;
  height: 40px;
  position: relative;
}

.button label,
.button input {
  padding: 5px 0 0 0;
  display: block;
  position: absolute;
  vertical-align: middle;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.button input[type="radio"] {
  opacity: 0.011;
  z-index: 100;
}

.button input[type="radio"]:checked + label {
  background: #935836;
  border-radius: 4px;
}

.button label {
  cursor: pointer;
  z-index: 90;
  line-height: 1.8em;
}
</style>
    
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
        fetch("csv/" + chartName + ".csv").then((result)=>{result.text().then((text)=>{
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
    const colors = [
        'rgba(255, 99, 132, 0.9)',
        'rgba(54, 162, 235, 0.9)',
        'rgba(255, 206, 86, 0.9)',
        'rgba(75, 192, 192, 0.9)',
        'rgba(153, 102, 255, 0.9)',
        'rgba(255, 159, 64, 0.9)'
    ];
    const elements = [
        'circle',
        'cross',
        'crossRot',
        'dash',
        'rect',
        'star',
        'triangle'
    ];
    const datasets = real_data.map((x,i)=>{
        return {
            label: real_names[i],
            data: x,
            backgroundColor: colors[i],
            borderColor: colors[i],
            borderWidth: 1,
            fill: false,
            pointStyle: elements[i],
            radius: 4,
        }
    });
    const data = {
        labels: labels,
        datasets: datasets,
    };
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
                        text: 'seconds',
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