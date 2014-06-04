$(document).ready(function() {
    setupDirectoryDropdown();
    initValidation();
});

function setupDirectoryDropdown() {
    $('input#dir').select2({
        minimumInputLength: 3,
        formatSelection: function (o) {
            return o.directory
        },
        formatResult: function (o) {
            return o.directory
        },
        query: function (query) {
            autocompleteDelay.ajaxFunction = Dajaxice.apps.filesystem.directories_autocomplete;
            autocompleteDelay.callback = query.callback;
            autocompleteDelay.errorCallback = function() {
                alert('Error: Could not fetch directory list.');
            };
            autocompleteDelay.queryUpdate(query.term);
        }
    });
}

function initValidation() {
    $('#fileform').validate({
        rules: {
            'name': {
                required: true,
                maxlength: 255
            },
            'dir': {
                required: true
            }
        },
        highlight: function (element) {
            $(element).closest('.control-group').removeClass('success').addClass('error');
        },
        success: function (element) {
            element.addClass('valid').closest('.control-group').removeClass('error').addClass("invisiblevalid");
        },
        ignore: ''
    });
}
