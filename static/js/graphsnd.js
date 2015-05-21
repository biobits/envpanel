/*queue()
    .defer(d3.json, "/locations/3")
    .await(makeGraphs);*/
getStats(3)

function getStats(idloc) {
    idloc = typeof idloc !== 'undefined' ? idloc : 3;
   // queue()
    //.defer(d3.json, "/locations/"+idloc)
    //.await(makeGraphs);

    d3.json("/locations/"+idloc, function(error, json) {
    if (error) return console.warn(error);
    locations = json;
    makeGraphs(error, locations);
});
};

function tempCol(temp) {
    col='#B276B2'
    if(temp>=0 & temp<= 20)
        col="#60BD68"
    else if (temp >20 & temp<26)
        col="#DECF3F"
    else if (temp >= 26)
        col="#F15854"
    return col
}

function makeGraphs(error, locations) {

    var dateFormat = d3.time.format("%Y-%m-%dT%H:%M:%S")//d3.time.format("%Y-%m-%d %H:%M:%S");
    var data = [{
        key: 'Temperatur [°C]',
        color2: '#7777ff',
        color: '#B276B2',
        area: true,
        values : []
    }];
    locations.forEach(function(d) {
    var tst=d[0].split('.')[0];
    var ts=dateFormat.parse(tst);
        d[0]=ts;

        data[0].values.push({x: ts, y:d[2]});
        //data[0].color.push(tempCol(d[2]))
    })
    //data[0].push({color: '#7777ff',area: true});

    var timest_akt=locations[locations.length-1][0];
    var temp_akt=locations[locations.length-1 ][2] ;
    var temp_hum=locations[locations.length-1][3];
    // Ortsbeschreibung des Sensors
    var ort_akt=$("#orte :selected").text()
    d_format=d3.time.format("%Y-%m-%d");
    t_format=d3.time.format("%H:%M:%S");

    d3.select("#date_akt").html(d_format(timest_akt));
    d3.select("#time_akt").html(t_format(timest_akt));
    d3.select("#temp_akt").html(temp_akt+ " °C");
    d3.select("#hum_akt").html(temp_hum +"%");
    d3.select("#aktort").html(ort_akt);
    nv.addGraph(function() {
  var chart = nv.models.lineChart()
    .useInteractiveGuideline(true)
    //.x(function(d) { return d[0] })
    //.y(function(d) { return d[2] })
   // .xScale(d3.time.scale())


    ;
    var tickMultiFormat = d3.time.format.multi([
            ["%-I:%M%p", function(d) { return d.getMinutes(); }], // not the beginning of the hour
            ["%-I%p", function(d) { return d.getHours(); }], // not midnight
            ["%b %-d", function(d) { return d.getDate() != 1; }], // not the first of the month
            ["%b %-d", function(d) { return d.getMonth(); }], // not Jan 1st
            ["%Y", function() { return true; }]
        ]);
        chart.xAxis
                .showMaxMin(false)
                .tickPadding(6)
                //.tickFormat(function (d) { return tickMultiFormat(new Date(d)); })
               .tickFormat(function (d) {return d3.time.format('%Y-%m-%d %H:%M')(new Date(d)); })
//  chart.xAxis
//    .axisLabel('Time')
//    .tickFormat(d3.time.scale())
    ;

  chart.yAxis
    .axisLabel('Temp [°C]')
    .tickFormat(d3.format('.2f'))
    ;

  d3.select('#tmphist svg')
    .datum(data)
    .transition().duration(500)
    .call(chart)
    ;

  nv.utils.windowResize(chart.update);

  return chart;
});
};

$("#orte").change(function () {
        var locid = this.value;
        getStats(locid);

    });