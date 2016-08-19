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

$( "#deleteProject" ).click(function(){
    $( "#deleteProject" ).replaceWith( '<button id="confirmDelete" type="button">i\'m sure!</button>' );
    $( "#confirmDelete" ).click(function(){
        $.post("/project", { name: thisProject, action: 'delete' }, function( data ){
            window.location.replace(data.redirect);
        });
    });
});