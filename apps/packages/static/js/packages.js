$(document).ready(function() {
    $('#savePackageButton').on('click', savePackage);
    $('.blacklistToggle').on('click', toggle);
});

function savePackage() {
    var $packageForm = $("#packageform");
    if ($packageForm.valid()) {
        $packageForm.submit();
    }
}

function toggle() {
    var id = $(this).data('version-id');
    $.ajax({
        url: "/versions/" + id + "/toggle",
        statusCode: {
            200: function (data, status, jqXHR) {
                var query = "table#versions > tbody > tr#version" + id + " > td:nth-child(5) > button";
                $(query).text(data)
            }
        }
    });
}
