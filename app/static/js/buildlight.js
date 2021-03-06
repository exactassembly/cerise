var builders = $.get("/api/builders", createTable());
var keys;
var buildsContext = {};

function createTable(){
    if (typeof thisProject !== 'undefined') { // if buildlight is invoked on /project page, where "thisProject" is defined inline
        var keys = [];
        keys.push(thisProject);
        if (subProjects){
            for (i = 0; i < subProjects.length; i++) {
                keys.push(thisProject + "-" + subProjects[i].name);
        }}
    }
    else {
        var keys = Object.keys(builders);
    }
    for (i = 0; i < keys.length; i++) {
        var b = builders[keys[i]];
        buildsContext[keys[i]] = [];
        $.get("/api/builders/" + b + "/builds?select=-1&select=-2&select=-3&select=-4&select=-5",
        function( data ){
            var builds = data;
            var buildKeys = Object.keys(builds);
            $('#build-light').append('<tr id="' + keys[i] + '">');
            $('#' + keys[i]).append('<th><a href="/api/force/' + keys[i] + '>' + keys[i] + '</a></th>');
            for (i = 0; i < buildKeys.length; i++) {
                var thisBuild = builds[buildKeys[i]];
                var buildNumber = thisBuild.number
                buildsContext[keys[i]].push(buildNumber); // buildsContext is now a collection of builds for user's current view
                if (thisBuild.error == 'undefined') { // if thisBuild isn't errored.  thisBuild will return an error with fewer than 5 builds
                    $('#' + keys[i]).append('<td id="build' + buildNumber + '"><a href="/api/log/' + thisBuild + '/' + buildNumber + '">' + thisBuild.text[1] + '</a></td>');
                }
            }
            $('#build-light').append('</tr>');
        });
    }
}

function updateTable(){
    for (i = 0; i < keys.length; i++) {
        var u = "/api/builders/" + keys[i] + "/builds?select=" + buildsContext[keys[i]][0]; // format first with '?'
        for (n = 1; n < buildsContext[keys[i]].length ; i++) { // start at 1
            u = u + "&select=" + buildsContext[keys[i]][n];
        }
        $.get(u, function( data ){
            var updateKeys = Object.keys(data);
            for (i = 0; i < updateKeys; i++) {
                $('#build' + data[updateKeys[i]]).text( data[updateKeys[i]] );            
            }
        });
    }
}

var interval = setInterval(updateTable, 5000);
