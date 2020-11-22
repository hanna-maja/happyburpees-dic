$("#search").keyup(function() {
    let term = $(this).val();
    $.get("/sok/" + term, function(data) {
        $( "#dictionary-items" ).html(data);
    });
});