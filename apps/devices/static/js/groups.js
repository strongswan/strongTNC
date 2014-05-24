$(document).ready(function() {
    initValidation();

    $('#groupSaveButton').on('click', saveGroup);
    $('#addMemberButton').on('click', addMember);
    $('#removeMemberButton').on('click', removeMember);
    $('#device_select').popover();
    $('#member_select').popover();
});

function saveGroup() {
    var $groupform = $("#groupform");
    var id = 'memberlist';
    if ($groupform.valid()) {
        $('#'+id).remove();
        $('<input />').attr('type', 'hidden').attr('id',id).attr('name', id).attr('value',
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

function initValidation() {
    $('#groupform').validate({
        onkeyup: false,
        rules: {
            'name': {
                required: true,
                maxlength: 255,
                remote: {
                    url: "/groups/check",
                    type: "post",
                    data: {
                        group: function () {
                            return $('#groupId').val();
                        },
                        name: function () {
                            return $("#name").val();
                        },
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]', '#groupform').val()
                    }
                }
            }
        },
        messages: {
            'name': {
                remote: "A group with this name already exists!"
            }
        },
        highlight: function (element) {
            $(element).closest('.control-group').removeClass('success').addClass('error');
        },
        success: function (element) {
            element.addClass('valid').closest('.control-group').removeClass('error').addClass('success');
        }
    });
}