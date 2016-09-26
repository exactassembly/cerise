$( "div #view" ).html('<iframe src="/buildlight"></iframe>');

$( "#addProject" ).click(function(){
    $( "div #view" ).html('<iframe src="/account/add"></iframe>');
});

$( "#addSub" ).click(function(){
    var project = $(this).attr('project');    
    $( "div #view" ).html('<iframe src="/account/add?parent=' + project + '></iframe>');
});

$( ".project-btn" ).click(function(){
    var project = $(this).attr('project');
    var sub = $(this).attr('subProj');
    if (sub){
        $( "div #view" ).html('<iframe src="/project?group=' + group + 'id=' + project + '&sub=' + sub + '></iframe>');
    }
    else {
        $( "div #view" ).html('<iframe src="/project?group=' + group + 'id=' + project + '></iframe>');
    }
});
