var HTTPport = user.port_offset + 20000;
var masterAddress = "window.location.hostname" + ":" + HTTPport;
var builders = $.get(masterAddress + "json/builders", createTable());
var keys;
var buildsContext = {};

function createTable(){
    var keys = Object.keys(builders);
    for (i = 0; i < keys.length; i++) {
        var b = builders[keys[i]];
        buildsContext[keys[i]] = [];
        $.get(masterAddress + "/json/builders/" + b + "/builds?select=-1&select=-2&select=-3&select=-4&select=-5",
        function( data ){
            var builds = data;
            var buildKeys = Object.keys(builds);
            $('#build-light').append('<tr id="' + keys[i] + '">');
            $('#' + keys[i]).append('<th>' + keys[i] + '</th>');
            for (i = 0; i < buildKeys.length; i++) {
                var thisBuild = builds[buildKeys[i]];
                var buildNumber = thisBuild.number
                buildsContext[keys[i]].push(buildNumber); // buildsContext is now a collection of builds for user's current view
                if (thisBuild.error == 'undefined') { // if thisBuild isn't errored.  thisBuild will return an error with fewer than 5 builds
                    $('#' + keys[i]).append('<td id="build' + buildNumber + '"><a href="' + masterAddress + '/builders/' + b + '/builds/' + buildNumber + '">' + thisBuild.text[1] + '</a></td>');
                }
            }
            $('#build-light').append('</tr>');
        });
    }
};

function updateTable(){
    for (i = 0; i < keys.length; i++) {
        var u = masterAddress + "/json/builders/" + keys[i] + "/builds?select=" + buildsContext[keys[i]][0]; // format first with '?'
        for (n = 1; n < buildsContext[keys[i]].length ; i++) { // start at 1
            u = u + "&select=" + buildsContext[keys[i]][n];
        }
        $.get(u, function( data ){
            var updateKeys = Object.keys(data);
            for (i = 0; i < updateKeys; i++) {
                $('#build' + data[updateKeys[i]]).text( data[updateKeys[i]].text )            
            }
        });
    }
};


var interval = setInterval(updateTable, 5000);
