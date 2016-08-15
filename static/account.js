$( "#addProject" ).click(function(){
    $( "#newProject" ).css('display', 'inline');
    $( "#addProject" ).css('display', 'none');
});

$( ".projectForm" ).submit(function( event ){
    payload = {};
    payload.name = $( this ).attr("id");
    payload.gitrepo = $( this ).children(".gitRepo");
    payload.steps = {};
    $( this ).children(".steps").children("li").each(function(index, value){
        payload.steps[index] = value;
    })
    $.post( "/account", payload, function(){
        location.reload();
    });
});