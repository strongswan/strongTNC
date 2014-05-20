$(document).ready(function() {
    $('#saveDeviceButton').on('click', saveDevice);
});

function saveDevice() {
    $('<input />').attr('type', 'hidden').attr('name', 'memberlist').attr('value',
        $("#group_select2").find("option:selected").map(function () {
            return this.value;
        }).get().join()).appendTo("#deviceform");
}