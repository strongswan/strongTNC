$(document).ready(function() {
    $('#saveProductButton').on('click', saveProduct);
});

function saveProduct() {
    $('<input />').attr('type', 'hidden').attr('name', 'defaultlist').attr('value',
        $("#group_select").find("option:selected").map(function () {
            return this.value;
        }).get().join()).appendTo("#productform");
}