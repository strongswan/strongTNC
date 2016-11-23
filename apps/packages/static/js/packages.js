$(document).ready(function () {
    initValidation();

    $('#savePackageButton').on('click', savePackage);
    $('#savePackageChanges').on('click', savePackageChanges);
    $('#addVersionSave').on('click', saveNewVersion);
});

function saveNewVersion() {
    var $versionForm = $("#newVersionForm");
    if ($versionForm.valid()) {
        $versionForm.submit();
    }
}


function savePackageChanges() {
    var versionFlags = [];
    $("tbody", "#versions").find('tr').each(function () {
        var row = $(this);
        versionFlags.push({
            id: row.prop("id"),
            security: row.find(".securityToggle").prop("checked"),
            blacklist: row.find(".blacklistToggle").prop("checked")
        });
    });
    $("#versionData").val(JSON.stringify(versionFlags));
    $("#packageform").submit();
}

function savePackage() {
    var $packageForm = $("#packageform");
    if ($packageForm.valid()) {
        $packageForm.submit();
    }
}

function initValidation() {
    $('#packageform').validate($.extend(validationDefaults, {
        rules: {
            'name': {
                required: true,
                maxlength: 255,
                remote: {
                    url: "/packages/check",
                    type: "post",
                    data: {
                        'package': function () {
                            return $('#packageId').val()
                        },
                        'name': function () {
                            return $("#name").val()
                        },
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]', '#packageform').val()
                    }
                }
            }
        },
        messages: {
            name: {
                remote: "Package already exists!"
            }
        },
        ignore: ":hidden:not(.select2-offscreen)"
    }));

    $('#newVersionForm').validate($.extend(validationDefaults, {
        rules: {
            'version': {
                required: true,
                maxlength: 255
            },
            'product': {
                required: true,
                regex: /^[0-9]+$/
            }
        },
        ignore: ":hidden:not(.select2-offscreen)"
    }));
}
