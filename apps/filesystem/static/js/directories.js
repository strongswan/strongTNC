$(document).ready(function() {
    initValidation();
});

function initValidation() {
    $('#directoryform').validate({
        rules: {
            'path': {
                required: true,
                maxlength: 255,
                directory: true,
                remote: {
                    url: "/directories/check",
                    type: "post",
                    data: {
                        'directory': function () {
                            return $('#directoryId').val()
                        },
                        'path': function () {
                            return $("#path").val()
                        },
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]', '#directoryform').val()
                    }
                }
            }
        },
        messages: {
            path: {
                remote: "Directory already exists!"
            }
        },
        highlight: function (element) {
            $(element).closest('.control-group').removeClass('success').addClass('error');
        },
        success: function (element) {
            element.addClass('valid').closest('.control-group').removeClass('error').addClass("invisiblevalid");
        }
    });
}