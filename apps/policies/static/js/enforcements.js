$(document).ready(function() {
    initValidation();
    // validate select2 dropdowns on change
    $('.slct2-dropdown', '#enforcementform').on('change', function() {$(this).valid();});
});

function initValidation() {
    $('#enforcementform').validate($.extend(validationDefaults, {
        rules: {
            'policy': {
                required: true,
                remote: {
                    url: "/enforcements/check",
                    type: "post",
                    data: {
                        policy: function () {
                            return $("#policy").val()
                        },
                        group: function () {
                            return $("#group").val()
                        },
                        enforcement: function () {
                            return $("#enforcementId").val()
                        },
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]', '#enforcementform').val()
                    }
                }
            },
            'group': {
                required: true,
                remote: {
                    url: "/enforcements/check",
                    type: "post",
                    data: {
                        policy: function () {
                            return $("#policy").val()
                        },
                        group: function () {
                            return $("#group").val()
                        },
                        enforcement: function () {
                            return $("#enforcementId").val()
                        },
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]', '#enforcementform').val()
                    }
                }
            },
            'max_age': {
                required: true,
                range: [0, 9223372036854775] // sqlite max value
            }
        },
        messages: {
            group: {
                remote: "Enforcement already exists!"
            },
            policy: {
                remote: "Enforcement already exists!"
            }
        }
    }));
}