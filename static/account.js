$( "#addProject" ).click(function(){
    $( "#newProject" ).css('display', 'inline');
    $( "#addProject" ).css('display', 'none');
});

$( "#newProject" ).submit(function( event ){
    payload = {};
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