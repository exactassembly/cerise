$( "#addProject" ).click(function(){
    $( "#projects" ).append( '
    <form id="newProject">\
        <input type="text" name="gitrepo">\
        <input type="text" name="step">\
        <button id="addStep" type="button">add step</button>\
        <button id="submit" type="submit">submit</button>\
    </form>' )
    
})