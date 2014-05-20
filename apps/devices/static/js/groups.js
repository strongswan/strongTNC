$(document).ready(function() {
    $('#groupSaveButton').on('click', saveGroup);
    $('#addMemberButton').on('click', addMember);
    $('#removeMemberButton').on('click', removeMember);
    $('#device_select').popover();
    $('#member_select').popover();
});

function saveGroup() {
    var $groupform = $("#groupform");
    if ($groupform.valid()) {
        $('<input />').attr('type', 'hidden').attr('name', 'memberlist').attr('value',
            $("#member_select").find("option").map(function () {
                return this.value;
            }).get().join()).appendTo("#groupform");
        $groupform.submit()
    }
}

function addMember() {
    var $deviceSelect = $("#device_select");
    $deviceSelect.find("> option:selected").each(function (index, elem) {
        $("#member_select").append("<option value='" + elem.value + "'>" + elem.text + "</option>")
    });
    $deviceSelect.find("> option:selected").remove()
}

function removeMember() {
    var $memberSelect = $("#member_select");
    $memberSelect.find("> option:selected").each(function (index, elem) {
        $("#device_select").append("<option value='" + elem.value + "'>" + elem.text + "</option>")
    });
    $memberSelect.find("> option:selected").remove()
}