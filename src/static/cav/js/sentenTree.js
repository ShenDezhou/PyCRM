$(function() {

    var svg = d3.select("svg"),
        width = +svg.attr("width"),
        height = +svg.attr("height");

    var color = d3.scaleOrdinal(d3.schemeCategory20);
    
    var size$1 = new Array();
    for (var i = 8; i < 20; i++) {
        size$1.push();
    };
    var size = d3.scaleOrdinal(size$1);

    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(function(d) {
            return d.id; }))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));

    d3.json("sentenTree.json", function(error, graph) {
        if (error) throw error;

        var link = svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(graph.links)
            .enter().append("line")
            .attr("stroke-width", function(d) {
                return Math.sqrt(d.value); });

        var node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(graph.nodes)
            .enter().append("circle")
            .attr("r",function(d) {
                return (Math.sqrt(parseInt(d.count)/1000)).toFixed(); })
            .attr("fill", function(d) {
                return color(d.group); })
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        
        // node.append("title")
        //     .text(function (d) {
        //         return d.id;
        //     });

        var node_text = svg.append("g")
            .attr("class", "text")
            .selectAll("text")
            .data(graph.nodes)
            .enter().append("text")
            .attr("fill",function(d) {
                return color(d.group); })
            .attr("style",function(d) {
                return "font-size:"+(parseInt(d.count)/1000).toFixed()+"px"; })
            .text(function(d) {
                return d.id; });

        simulation
            .nodes(graph.nodes)
            .on("tick", ticked);

        simulation.force("link")
            .links(graph.links);

        function ticked() {
            link
                .attr("x1", function(d) {
                    return d.source.x; })
                .attr("y1", function(d) {
                    return d.source.y; })
                .attr("x2", function(d) {
                    return d.target.x; })
                .attr("y2", function(d) {
                    return d.target.y; });

            node
                .attr("cx", function(d) {
                    return d.x; })
                .attr("cy", function(d) {
                    return d.y; });

            node_text
                .attr("x", function(d) {
                    return d.x; })
                .attr("y", function(d) {
                    return d.y; });
        }
    });

    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
});
