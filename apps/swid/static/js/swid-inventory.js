var session_data = [];

function AjaxTagsLoader() {
    this.loadTags = function (sessionID) {
        var pager = $('.ajax-paged').data('pager');
        pager.reset();
        pager.setProducerArgs({'session_id': sessionID});
        pager.getPage();

        Dajaxice.apps.swid.get_tag_stats(this.updateStats, {
            'session_id': sessionID
        });
    };

    this.updateStats = function (data) {
        $("#swid-tag-count").text(data['swid-tag-count']);
        $("#swid-newtag-count").text(data['new-swid-tag-count']);
    };
}

function AjaxSessionsLoader() {
    this.deviceId = $("#device-id").val();
    this.updateSelect = function (data) {
        ajaxSpinner.disable();
        session_data = data.sessions;
        $("#num-of-sessions").text(data.sessions.length);
    };

    this.loadSessions = function () {
        var fromTimestamp = parseInt(HashQuery.getHashQueryObject()['from']);
        var toTimestamp = parseInt(HashQuery.getHashQueryObject()['to']);
        if (!fromTimestamp || !toTimestamp) return;
        ajaxSpinner.enable();
        Dajaxice.apps.devices.sessions_for_device(this.updateSelect, {
            'device_id': this.deviceId,
            'date_from': fromTimestamp,
            'date_to': toTimestamp
        });
    };
}

function setupResetButton() {
    $("#session-filter-reset").click(function () {
        $("#calendar-shortcuts").prop("selectedIndex", 1);
    })
}

function setupRangeShortcutsDropdown(fromDatepicker, toDatepicker) {
    $("#calendar-shortcuts").change(function () {
            fromDatepicker.datepicker("setDate", $(this).val());
            toDatepicker.datepicker("setDate", new Date());
            HashQuery.setHashKey({
                'from': fromDatepicker.datepicker("getDate").getTime() / 1000,
                'to': toDatepicker.datepicker("getDate").getTime() / 1000
            }, true);

            HashQuery.sendChanged('from', fromDatepicker.datepicker("getDate"));
        }
    );
}

function setUpSelect() {
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
            formatNoMatches: "No Session found in the given time range"
        }
    );
    $("#sessions").on("select2-selecting", function (event) {
        HashQuery.setHashKey({'session-id': event.val})
    });
}

function setupDatepicker(fromDatepicker, toDatepicker) {
    fromDatepicker.datepicker({
        defaultDate: "-1w",
        dateFormat: "dd/mm/yy",
        changeMonth: true,
        numberOfMonths: 1,
        onSelect: function (selectedDate) {
            toDatepicker.datepicker("option", "minDate", selectedDate);
            var fromTimestamp = $(this).datepicker("getDate").getTime() / 1000;
            HashQuery.setHashKey({'from': fromTimestamp});
        }
    });

    toDatepicker.datepicker({
        changeMonth: true,
        dateFormat: "dd/mm/yy",
        defaultDate: new Date(),
        numberOfMonths: 1,
        onSelect: function (selectedDate) {
            var toTimestamp = $(this).datepicker("getDate").getTime() / 1000;
            HashQuery.setHashKey({'to': toTimestamp});
            fromDatepicker.datepicker("option", "maxDate", selectedDate);
        }
    });

    fromDatepicker.datepicker("setDate", '-1w');
    toDatepicker.datepicker("setDate", new Date());

    $("#from-btn").click(function () {
        fromDatepicker.datepicker("show");
    });

    $("#to-btn").click(function () {
        toDatepicker.datepicker("show");
    });

}

function loadSingleSession(fromDatepicker, toDatepicker, sessionId) {
    Dajaxice.apps.swid.session_info(function (data) {

        $("#for-session").text(data.time);
        session_data = [
            {"id": data.id, "time": data.time}
        ];
        $("#sessions").select2("val", data.id);
        $("#num-of-sessions").text("1");
        fromDatepicker.datepicker("setDate", null);
        toDatepicker.datepicker("setDate", null);
        HashQuery.sendChanged('session-id', data.id);

    }, {
        'session_id': sessionId
    });
}

$(document).ready(function () {
    var fromDatepicker = $("#from");
    var toDatepicker = $("#to");
    var sessionDropdown = $("#sessions");

    $("#swid-tags").hide();
    var sessionsLoader = new AjaxSessionsLoader();
    var tagsLoader = new AjaxTagsLoader();

    // setup components
    setupDatepicker(fromDatepicker, toDatepicker);
    setUpSelect();
    setupRangeShortcutsDropdown(fromDatepicker, toDatepicker);
    setupResetButton();

    // register event listeners
    HashQuery.addChangedListener('session-id', function (key, value) {
        var logLink = $("#swid-log-link");
        var old_link = logLink.prop("href").split("#")[0];
        logLink.prop("href", old_link + "#session-id=" + value);

        tagsLoader.loadTags(value);
        var result = $.grep(session_data, function (e) {
            return e.id == value
        });

        // session-id is not available in the sessions dropdown
        if (!result.length) {
            var sessionId = HashQuery.getHashQueryObject()['session-id']
            loadSingleSession(fromDatepicker, toDatepicker, sessionId);
        }
        else {
            sessionDropdown.select2("val", value);
            var timeString = sessionDropdown.select2("data")["time"];
            $("#for-session").text(timeString);
        }
    });

    HashQuery.addChangedListener('from', function (key, value) {
        sessionsLoader.loadSessions();
    });

    HashQuery.addChangedListener('to', function (key, value) {
        sessionsLoader.loadSessions();
    });

    // view was called from session view
    if (HashQuery.getHashQueryObject()['session-id']) {
        var sessionId = HashQuery.getHashQueryObject()['session-id']
        loadSingleSession(fromDatepicker, toDatepicker, sessionId);
    }

});
