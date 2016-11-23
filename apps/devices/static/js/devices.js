$(document).ready(function () {
    initValidation();

    $('#saveDeviceButton').on('click', saveDevice);
    // validate select2 dropdowns on change
    $('.slct2-dropdown', '#deviceform').on('change', function () {
        $(this).valid();
    });
});

function saveDevice() {
    if ($(this).valid()) {
        var id = 'memberlist';
        $('#' + id).remove();
        $('<input />').attr('type', 'hidden').attr('id', id).attr('name', id).attr('value',
            $("#group_select2").find("option:selected").map(function () {
                return this.value;
            }).get().join()).appendTo("#deviceform");
    }
}

function initValidation() {
    $('#deviceform').validate($.extend(validationDefaults, {
        rules: {
            'value': {
                required: true,
                maxlength: 255,
                regex: /^[a-fA-F0-9]+$/,
                remote: {
                    url: "/devices/check",
                    type: "post",
                    data: {
                        value: function () {
                            return $("#value").val()
                        },
                        product: function () {
                            return $("#product").val()
                        },
                        device: function () {
                            return $("#deviceId").val()
                        },
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]', '#deviceform').val()
                    }
                }
            },
            'description': {
                required: true
            },
            'product': {
                required: true,
                remote: {
                    url: "/devices/check",
                    type: "post",
                    data: {
                        value: function () {
                            return $("#value").val()
                        },
                        product: function () {
                            return $("#product").val()
                        },
                        device: function () {
                            return $("#deviceId").val()
                        },
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]', '#deviceform').val()
                    }
                }
            },
            'group_select2': {
                required: true
            }
        },
        messages: {
            value: {
                regex: "Only HEX values allowed",
                remote: "Device already exists."
            },
            product: {
                remote: "Device already exists."
            }
        },
        ignore: ":hidden:not(.select2-offscreen)"
    }));
}