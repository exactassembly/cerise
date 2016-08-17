$( "#addProject" ).click(function(){
    $( "#newProject" ).css('display', 'inline');
    $( "#addProject" ).css('display', 'none');
});

$( "#addStep" ).click(function(){
    var index = $( "#steps" ).children().length;
    stepID = "steps-" + index + "-step"
    workdirID = "steps-" + index + "-workdir"
    $( "#steps" ).append(
    '<div>\
        <input id="' + stepID + '" name="' + stepID + '" type="text" placeholder="action"></input>\
        <input id="' + workdirID + '" name="' + workdirID + '" type="text" placeholder="workdir"></input>\
    </div>')     
})
