$( "#addProject" ).click(function(){
    $( "#newProject" ).css('display', 'inline');
    $( "#addProject" ).css('display', 'none');
})

$( "#project" ).submit(function( event ){
    payload = $( this ).serializeArray();
    $.post( "/account", { name: $.})
})