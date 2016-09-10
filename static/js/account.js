$( "div #main" ).html('<iframe src="/static/buildlight.html"></iframe>');

$( "#addProject" ).click(function(){
    $( "div #main" ).html('<iframe src="/account/add"></iframe>');
});

$( "#addSub" ).click(function(){
    var project = $(this).attr('project');    
    $( "div #main" ).html('<iframe src="/account/add?parent=' + project + '></iframe>');
});

$( ".project-btn" ).click(function(){
    var project = $(this).attr('project');
    var sub = $(this).attr('subProj');
    if (sub){
        $( "div #main" ).html('<iframe src="/project?currentProject=' + project + '&sub=' + sub + '></iframe>');
    }
    else {
        $( "div #main" ).html('<iframe src="/project?currentProject=' + project + '></iframe>');
    }
});