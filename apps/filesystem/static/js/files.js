$(document).ready(function() {
    setupDirectoryDropdown();
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
