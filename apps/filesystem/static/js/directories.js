$(document).ready(function() {
    initValidation();
});

function initValidation() {
    $('#directoryform').validate($.extend(validationDefaults, {
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
        }
    }));
}