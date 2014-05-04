var session_data = [];

function AjaxTagsLoader() {
    this.loadTags = function (sessionID) {
        ajaxSpinner.enable();
        Dajaxice.apps.swid.tags_for_session(this.fillTable, {
            'session_id': sessionID
        });
    }

    this.fillTable = function (data) {
        var tableBody = $("#swid-tags").find("tbody");
        $("#swid-tag-count").text(data['swid-tag-count']);
        tableBody.empty();
        var rows = '';
        $.each(data['swid-tags'], function (i, record) {
            rows +=
                "<tr><td>" +
                    record['name'] +
                    "</td><td>" +
                    record['version'] +
                    "</td><td>" +
                    record['unique-id'] +
                    "</td><td>" +
                    record['installed'] +
                    "</td></tr>";
        });
        tableBody.append(rows);
        ajaxSpinner.disable();
    }
}

function AjaxSessionsLoader(from, to) {
    this.deviceId = $("#device-id").val();
    this.fromDatepicker = from;
    this.toDatepicker = to;
    this.updateSelect = function (data) {
        ajaxSpinner.disable();
        session_data = data.sessions;
        $("#num-of-sessions").text(data.sessions.length);
    }

    this.loadSessions = function () {
        var fromTimestamp = Math.floor(this.fromDatepicker.datepicker("getDate").getTime() / 1000);
        var toTimestamp = Math.floor(this.toDatepicker.datepicker("getDate").getTime() / 1000);
        ajaxSpinner.enable();
        Dajaxice.apps.devices.sessions_for_device(this.updateSelect, {
            'device_id': this.deviceId,
            'date_from': fromTimestamp,
            'date_to': toTimestamp
        });
    }
}

function setupResetButton() {
    $("#session-filter-reset").click(function () {
        $("#calendar-shortcuts").prop("selectedIndex", 1);
    })
}

function setupRangeShortcutsDropdown(sessionManager) {
    $("#calendar-shortcuts").change(function () {
        $("#from").datepicker("setDate", $(this).val())
        $("#to").datepicker("setDate", new Date());
        $("#sessions").select2("val", "");
        sessionManager.loadSessions();
    });
}

function setUpSelect(tagLoader) {
    var convertResultToString = function (sessionObject) {
        return sessionObject.time;
    };

    $("#num-of-sessions").text(session_data.length);
    $('#sessions').select2({
            data: function () {
                return {
                    results: session_data,
                    text: 'time'
                }
            },
            formatSelection: convertResultToString,
            formatResult: convertResultToString,
            placeholder: "Select a Session",
            width: "element",
            minimumResultsForSearch: -1,
            formatNoMatches : "No Session found in the given time range"
        }
    );
    $("#sessions").on("select2-selecting", function (event) {
        tagLoader.loadTags(event.val);
    })
}


function setupDatepicker(sessionsLoader) {


    sessionsLoader.fromDatepicker.datepicker({
        defaultDate: "-1w",
        changeMonth: true,
        numberOfMonths: 1,
        onClose: function (selectedDate) {
            sessionsLoader.toDatepicker.datepicker("option", "minDate", selectedDate);
            sessionsLoader.loadSessions();
        }
    });

    sessionsLoader.toDatepicker.datepicker({
        changeMonth: true,
        numberOfMonths: 1,
        onClose: function (selectedDate) {
            sessionsLoader.fromDatepicker.datepicker("option", "maxDate", selectedDate);
            sessionsLoader.loadSessions()
        }
    });

    sessionsLoader.fromDatepicker.datepicker("setDate", '-1w');
    sessionsLoader.toDatepicker.datepicker("setDate", new Date());
}

$(document).ready(function () {
    var sessionsLoader = new AjaxSessionsLoader($("#from"), $("#to"))
    var tagsLoader = new AjaxTagsLoader();
    setUpSelect(tagsLoader);
    setupDatepicker(sessionsLoader);
    setupRangeShortcutsDropdown(sessionsLoader);
    setupResetButton();
});
