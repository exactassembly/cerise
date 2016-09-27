$( "div #view" ).html('<iframe src="/buildlight"></iframe>');

$( "#addProject" ).click(function(){
    var group = $(this).attr('group');        
    $( "div #view" ).html('<iframe src="/account/add?group=' + group + '"></iframe>');
});

$( "#addSub" ).click(function(){
    var group = $(this).attr('group');            
    var project = $(this).attr('project');    
    $( "div #view" ).html('<iframe src="/account/add?group=' + group + '&parent=' + project + '></iframe>');
});

$( ".project-btn" ).click(function(){
    var group = $(this).attr('group');   
    var project = $(this).attr('project');
    var sub = $(this).attr('sub');
    if (sub){
        $( "div #view" ).html('<iframe src="/project?group=' + group + '&project=' + project + '&sub=' + sub + '></iframe>');
    }
    else {
        $( "div #view" ).html('<iframe src="/project?group=' + group + '&project=' + project + '></iframe>');
    }
});
