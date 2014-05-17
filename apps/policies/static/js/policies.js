$(document).ready(function() {
    initValidation();

    typeChange();
    $('#type').on('change', typeChange);
    $('#savePolicyButton').on('click', savePolicy);

    // validate select2 dropdowns on change
    $('.slct2-dropdown', '#policyform').on('change', function() {$(this).valid();});
    $('.slct2-autocomplete', '#policyform').on('change', function() {$(this).valid();});

});

function savePolicy() {
    var $policyform = $('#policyform');
    if($policyform.valid()) {
        prepareFlags();
        var $form = $(this);
        $form.children('.filter:hidden').remove();
        $policyform.submit();
    }
}

var PolicyType = {
    PCKGS: 1,
    UNSRC: 2,
    FWDEN: 3,
    PWDEN: 4,
    FREFM: 5,
    FMEAS: 6,
    FMETA: 7,
    DREFM: 8,
    DMEAS: 9,
    DMETA: 10,
    TCPOP: 11,
    TCPBL: 12,
    UDPOP: 13,
    UDPBL: 14,
    SWIDT: 15,
    TPMRA: 16
};

function prepareFlags() {

    var $form = $('#policyform');
    var id = 'flags';
    $('#' + id, $form).remove();
    var $hiddenFlagInput = $('<input />').attr('type', 'hidden').attr('id',id).attr('name', id).appendTo($form);
    var value = "";
    var type = $('select#type').find('option:selected').attr("value");

    // swid-flags
    if (type == PolicyType.SWIDT) {
        value = $("#swidflags").val().join(' ');
    }
    // attestation-flags
    if (type == PolicyType.TPMRA) {
        value = $("#attestationflags").val().join(' ');
    }
    $hiddenFlagInput.val(value);

}

function typeChange() {
    var $fileContainer = $('#file-container').hide();
    var $dirContainer = $('#dir-container').hide();
    var $portContainer = $('#port-container').hide();
    var $openPortLabel = $('#open-port-label').hide();
    var $closedPortLabel = $('#closed-port-label').hide();
    var $swidRequest = $('#swid-request').hide();
    var $tpmAttest = $('#tpm-attestation').hide();

    var type = $('select#type').find('option:selected').attr("value");

    if (type == PolicyType.FREFM || type == PolicyType.FMEAS || type == PolicyType.FMETA) {
        $fileContainer.show();
    }
    else if (type == PolicyType.DREFM || type == PolicyType.DMEAS || type == PolicyType.DMETA) {
        $dirContainer.show();
    }
    else if (type == PolicyType.TCPOP || type == PolicyType.UDPOP) {
        $portContainer.show();
        $closedPortLabel.show();
    }
    else if (type == PolicyType.TCPBL || type == PolicyType.UDPBL) {
        $portContainer.show();
        $openPortLabel.show();
    }
    else if (type == PolicyType.SWIDT) {
        $swidRequest.show();
    }
    else if (type == PolicyType.TPMRA) {
        $tpmAttest.show();
    }
}

function initValidation() {
    $('#policyform').validate({
        ignore: '',
        rules: {
            'name': {
                required: true,
                maxlength: 255,
                remote: {
                    url: "/policies/check",
                    type: "post",
                    data: {
                        'policy': function () {
                            return $('#policyId').val()
                        },
                        'name': function () {
                            return $("#name").val()
                        },
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]', '#policyform').val()
                    }
                }
            },
            'type': {
                required: true,
                regex: /^[0-9]+$/
            },
            'range': {
                required: {
                    depends: function (element) {
                        var type = $("#type").val();
                        return type == PolicyType.TCPBL || type == PolicyType.TCPOP || type == PolicyType.UDPBL || type == PolicyType.UDPOP;
                    }
                },
                regex: /^ *\d+ *(- *\d+ *)?( *,*( *\d+ *)( *- *\d+ *)?)*$/
            },
            'file': {
                required: {
                    depends: function (element) {
                        var type = $("#type").val();
                        return type == PolicyType.FREFM || type == PolicyType.FMEAS || type == PolicyType.FMETA;
                    }
                }
            },
            'dir': {
                required: {
                    depends: function (element) {
                        var type = $("#type").val();
                        return type == PolicyType.DREFM || type == PolicyType.DMEAS || type == PolicyType.DMETA;
                    }
                }
            },
            'swidflags': {
                required: {
                    depends: function (element) {
                        var type = $("#type").val();
                        return type == PolicyType.SWIDT;
                    }
                }
            },
            'attestationflags': {
                required: {
                    depends: function (element) {
                        var type = $("#type").val();
                        return type == PolicyType.TPMRA;
                    }
                }
            },
            'fail': {
                required: true
            },
            'noresult': {
                required: true
            }
        },
        messages: {
            name: {
                remote: "A policy with this name already exists!"
            },
            type: {
                regex: "This field is required."
            },
            'file': {
                required: "This field is required."
            }
        },
        highlight: function (element) {
            $(element).closest('.control-group').removeClass('success').addClass('error');
        },
        success: function (element) {
            element.addClass('valid').closest('.control-group').removeClass('error').addClass("invisiblevalid");
        },
        errorPlacement: function (error, element) {
            if (element.attr("id") == "type") {
                error.insertAfter("#s2id_type");
            } else if (element.attr("id") == "fail") {
                error.insertAfter("#s2id_fail");
            } else if (element.attr("id") == "noresult") {
                error.insertAfter("#s2id_noresult");
            } else if (element.attr("id") == "file") {
                error.insertAfter("#s2id_file");
            } else if (element.attr("id") == "dir") {
                error.insertAfter("#s2id_dir");
            } else {
                error.insertAfter(element)
            }
        }
    });
}