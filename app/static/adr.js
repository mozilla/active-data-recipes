$(function() {
    $("#search").on("input",function(e) {
        var term = e.target.value;
        $("#recipes > a").each(function () {
            var element = $(this);
            var recipe_name = element.prop("id");
            if (recipe_name.indexOf(term) < 0) {
                element.hide();
            } else {
                element.show();
            }
        });
    });
});
