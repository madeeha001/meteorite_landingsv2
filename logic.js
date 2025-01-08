const API_URL = "http://127.0.0.1:5000/api/v1.0/meteorite-landings/unique-years";

function init()
{
    // Use d3 to select the dropdown with id of `#selDataset
    
    d3.json("http://127.0.0.1:5000/api/v1.0/meteorite-landings/unique-years").then((data)=>{
        let years = data.unique_years;
        console.log(years);
        let dropdown_year = d3.select("#selDataset");
        for(i of years){
            dropdown_year.append("option").attr("value", i).text(i);
          };
        //buildBar(years[0]);
        buildBar(1851);
        mapByYear(1851);
        statsYear(1851)
    });
    

    d3.json("http://127.0.0.1:5000/api/v1.0/meteorite-landings/unique-names").then((data)=>{
        let names = data.unique_names; 
        let dropdown_name = d3.select("#selName");
        for(n of names){
            dropdown_name.append("option").attr("value", n).text(n);
        };

    });
    //console.log(year);
    buildTopYearCountBar();
    printStatistics()


}
init();

function buildTopYearCountBar()
{
    const url="http://127.0.0.1:5000/api/v1.0/meteorite-landings/top-years";
    d3.json(url).then((data)=>{
        //console.log(data[0])
        //let mapArrow2 = theStagesOfJS.map(item => item);
        let year = data.map(doc => doc.year);
        const stringYear = year.map(String);
        let year_count = data.map(doc => doc.count);
        console.log(year_count);
        let bar_trace = {
            x: stringYear,
            y: year_count,
            type: 'bar'
          };
          
          let data_plot = [bar_trace];
          
          let layout = {
            title: "Top 10 Years Count"
          };
          
          Plotly.newPlot("plot-top", data_plot, layout);
    });
}


function buildBar(sample)
{
    let url="http://127.0.0.1:5000/api/v1.0/meteorite-landings/year/"+sample;
    d3.json(url).then((data)=>{
        //console.log(data[0])
        //let mapArrow2 = theStagesOfJS.map(item => item);
        let names = data.map(doc => doc.name);
        //console.log(names);
        let m="mass (g)";
        let mass = data.map(doc => doc.mass);
        console.log(mass);
        let bar_trace = {
            x: names,
            y: mass,
            type: 'bar'
          };
          
          let data_plot = [bar_trace];
          
          let layout = {
            title: `By Year ${sample}`
          };
          
          Plotly.newPlot("plot", data_plot, layout);
    });
}

function statsYear(year)
{
    console.log(year)
    let url= "http://127.0.0.1:5000/api/v1.0/meteorite-landings/stats-year/"+year;
    d3.json(url).then((data) => {
        console.log(data);
       
        // Use d3 to select the panel with id of `#sample-metadata`
        year_stats= d3.select('#stats-year');
    
        year_stats.text("");
        // Object.entries(data).forEach(([key,value]) => {
        //   console.log(key,value);
        //   //select the demographic info html section with d3 and append new key-value pair
        //   year_stats.append('h2').text(`${key}: ${value}`);
        // });
        let stat="Selected Year: "+data.year+"  Count: ("+data.count+")  Max Mass: "+data.max_mass+"  Min Mass: "+data.min_mass;
        year_stats.append('h3').text(stat);
    
        // Inside a loop, you will need to use d3 to append new
        // tags for each key-value in the filtered metadata.
    
      });
}


function printStatistics()
{
    
    let url= "http://127.0.0.1:5000/api/v1.0/meteorite-landings/statistics";
    d3.json(url).then((data) => {
        console.log(data);
       
        // Use d3 to select the panel with id of `#statistics`
       stats_land= d3.select('#statistics');
    
        stats_land.text("");
        stats_land.append('h4').text(`Total Years: ${data.total_years}`);
        stats_land.append('h4').text(`Total Meteorites: ${data.total_meteorites}`);
        stats_land.append('h4').text(`Maximum Mass: ${data.max_mass}`);
        stats_land.append('h4').text(`Average Mass: ${data.average_mass}`);
        stats_land.append('h4').text(`Minimum Mass: ${data.min_mass}`);
    
        // Inside a loop, you will need to use d3 to append new
        // tags for each key-value in the filtered metadata.
    
      });
}




function nameData(name)
{
    console.log(name)
    let url= "http://127.0.0.1:5000/api/v1.0/meteorite-landings/"+name;
    d3.json(url).then((data) => {
        console.log(data[0]);
       
        // Use d3 to select the panel with id of `#sample-metadata`
        sample_meta= d3.select('#name-info');
    
        sample_meta.text("");
        Object.entries(data[0]).forEach(([key,value]) => {
          console.log(key,value);
          //select the demographic info html section with d3 and append new key-value pair
          sample_meta.append('p').text(`${key.toUpperCase()}: ${value}`);
        });
    
    
        // Inside a loop, you will need to use d3 to append new
        // tags for each key-value in the filtered metadata.
    
      });
}


// Declare the map object and LayerGroup globally
let myMap;
let markerLayer;

function mapByYear(year) {
    const url = `http://127.0.0.1:5000/api/v1.0/meteorite-landings/map/year/${year}`;
    d3.json(url).then((data) => {
        // Initialize the map only once
        if (!myMap) {
            myMap = L.map("map", {
                center: [0, 0], // Default center
                zoom: 2
            });

            // Add a tile layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(myMap);

            // Initialize a LayerGroup for markers
            markerLayer = L.layerGroup().addTo(myMap);
        }

        // Clear the existing markers
        markerLayer.clearLayers();

        // Add new markers to the map
        for (let i = 0; i < data.length; i++) {
            let doc = data[i];
            const popupContent = `<h1>${doc.name}</h1> <hr> 
                                  <h3>Mass: ${doc.mass.toLocaleString()}</h3>
                                  <h4>Class: ${doc.recclass}</h4>
                                  <h4>Geo Location: ${doc.GeoLocation}</h4>`;
            L.marker(doc.GeoLocation, { draggable: false })
                .bindPopup(popupContent)
                .addTo(markerLayer);
        }

        // Update the map center dynamically based on the first point
        if (data.length > 0) {
            myMap.setView(data[0].GeoLocation, 5);
        }
    });
}

function optionChangedYear(newSample) {
    console.log("Value Selected: ", newSample);
    buildBar(newSample);
    mapByYear(newSample);
    statsYear(newSample)

  }

function optionChangedName(name)
{
    console.log("Name Selected: ", name);
    nameData(name);

}




