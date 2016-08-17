$( "#addProject" ).click(function(){
    $( "#newProject" ).css('display', 'inline');
    $( "#addProject" ).css('display', 'none');
});

$( "#addStep" ).click(function(){
    var index = $( "#steps" ).children().length
    index = index+1
    $( "#steps" ).append(String.format('<input id="steps-{0} name="steps-{0}" type="text"></input>', index))
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