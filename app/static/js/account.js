$( "div #view" ).html('<iframe src="/buildlight"></iframe>');

$( "#addProject" ).click(function(){
    var group = $(this).attr('data-group');        
    $( "div #view" ).html('<iframe src="/account/add?group=' + group + '"></iframe>');
});

$( "#addSub" ).click(function(){
    var group = $(this).attr('data-group');            
    var project = $(this).attr('data-project');    
    $( "div #view" ).html('<iframe src="/account/add?group=' + group + '&parent=' + project + '></iframe>');
});

$( ".project-btn" ).click(function(){
    var group = $(this).attr('data-group');   
    var project = $(this).attr('data-project');
    var sub = $(this).attr('data-sub');
    if (sub){
        $( "div #view" ).html('<iframe src="/project?group=' + group + '&project=' + project + '&sub=' + sub + '></iframe>');
    }
    else {
        $( "div #view" ).html('<iframe src="/project?group=' + group + '&project=' + project + '></iframe>');
    }
});
