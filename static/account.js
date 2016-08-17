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
        <input id="' + stepID + '" name="' + stepID + '" type="text"></input>\
        <input id="' + workdirID + '" name="' + workdirID + '" type="text"></input>\
    </div>')     
})

$( "#newProject" ).submit(function( event ){
    event.preventDefault();
    var payload = {};
    payload.name = $( this ).children("#name");
    payload.gitrepo = $( this ).children("#gitrepo");
    payload.steps = {};
    $( this ).children(".steps").children("li").each(function(index, value){
        payload.steps[index] = value;
    })
    $.post( "/account", payload, function(){
        location.reload();
    });
});