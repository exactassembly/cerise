$( "#addStep" ).click(function(){
    var index = $( "#steps" ).children().length;
    stepID = "steps-" + index + "-step"
    workdirID = "steps-" + index + "-workdir"
    $( "#steps" ).append(
    '<div>\
        <input id="' + stepID + '" name="' + stepID + '" type="text" placeholder="action"></input>\
        <input id="' + workdirID + '" name="' + workdirID + '" type="text" placeholder="workdir"></input>\
    </div>')     
});

$( "#addRepo" ).click(function(){
    var index = $( "#sourceRepos" ).children().length;
    nameID = "subs-" + index + "-name"
    urlID = "subs-" + index + "-url"
    $( "#sourceRepos" ).append(
    '<div>\
        <input id="' + nameID + '" name="' + nameID + '" type="text" placeholder="name"></input>\
        <input id="' + urlID + '" name="' + urlID + '" type="text" placeholder="url"></input>\
    </div>')     
});

$( "#deleteProject" ).click(function(){
    $( "#deleteProject" ).replaceWith( '<button id="confirmDelete" type="button">i\'m sure!</button>' );
    $( "#confirmDelete" ).click(function(){
        $.post("/project", { name: thisProject, action: 'delete' }, function( data ){
            window.location.replace('/account');
        });
    });
});