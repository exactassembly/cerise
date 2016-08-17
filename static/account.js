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
    var payload;
    var payload.name = $( this ).children("#name");
    var payload.gitrepo = $( this ).children("#gitrepo");
    var payload.steps = {};
    $( this ).children(".steps").children("li").each(function(index, value){
        var payload.steps[index] = value;
    })
    $.post( "/account", payload, function(){
        location.reload();
    });
});