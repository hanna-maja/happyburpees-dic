$("#search").keyup(function() {
    let term = $(this).val();
    $.get("/sok/" + term, function(data) {
        $( "#dictionary-items" ).html(data);
    });
});

function setNavigation() {
    var path = window.location.pathname;
    path = path.replace(/\/$/, "");
    path = decodeURIComponent(path);
    $("#sidebar-wrapper a").each(function () {
        var href = $(this).attr('href');
        if (href == '/'){ // Exception for startpage
            if(path == ''){
                $(this).addClass('active');
            }
            else{
                $(this).removeClass('active');
            }
        }
        else if (path.substring(0, href.length) === href) {
            $(this).addClass('active');
        }
        else{
            $(this).removeClass('active');
        }
    });
}
$(document).ready(function(){
    setNavigation();
});
