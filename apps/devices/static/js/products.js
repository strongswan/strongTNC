$(document).ready(function () {
    initValidation();

    $('#saveProductButton').on('click', saveProduct);
});

function saveProduct() {
    var $productform = $('#productform');
    if ($productform.valid()) {
        var id = 'defaultlist';
        $('#' + id).remove();
        $('<input />').attr('type', 'hidden').attr('id', id).attr('name', id).attr('value',
            $("#group_select").find("option:selected").map(function () {
                return this.value;
            }).get().join()).appendTo($productform);
    }
}

function initValidation() {
    $('#productform').validate($.extend(validationDefaults, {
        rules: {
            'name': {
                required: true,
                maxlength: 255,
                remote: {
                    url: "/products/check",
                    type: "post",
                    data: {
                        'product': function () {
                            return $('#productId').val()
                        },
                        'name': function () {
                            return $("#name").val()
                        },
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]', '#productform').val()
                    }
                }
            },
            'group_select': {
                required: true
            }
        },
        messages: {
            name: {
                remote: "Product already exists!"
            }
        }
    }));
}