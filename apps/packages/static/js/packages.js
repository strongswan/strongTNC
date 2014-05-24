$(document).ready(function() {
    initValidation();

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
            200: function (data) {
                var query = "table#versions > tbody > tr#version" + id + " > td:nth-child(5) > button";
                $(query).text(data)
            }
        }
    });
}

function initValidation() {
    $('#packageform').validate({
        rules: {
            'name': {
                required: true,
                maxlength: 255,
                remote: {
                    url: "/packages/check",
                    type: "post",
                    data: {
                        'package': function () {
                            return $('#packageId').val()
                        },
                        'name': function () {
                            return $("#name").val()
                        },
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]', '#packageform').val()
                    }
                }
            }
        },
        messages: {
            name: {
                remote: "Package already exists!"
            }
        },
        highlight: function (element) {
            $(element).closest('.control-group').removeClass('success').addClass('error');
        },
        success: function (element) {
            element.addClass('valid').closest('.control-group').removeClass('error').addClass("invisiblevalid");
        },
        ignore: ":hidden:not(.select2-offscreen)"
    });
}
