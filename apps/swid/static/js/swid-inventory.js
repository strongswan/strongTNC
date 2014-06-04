
function AjaxTagsLoader() {
    this.loadTags = function (sessionID, $pagerContext) {
        var pager = $('.ajax-paged', $pagerContext).data('pager');
        pager.reset();
        pager.setProducerArgs({'session_id': sessionID});
        pager.getPage();
    };
}

function AjaxSessionsLoader() {
    this.deviceId = $("#device-id").val();

    this.loadSessions = function () {
        var fromTimestamp = parseInt(HashQuery.getHashQueryObject()['from']);
        var toTimestamp = parseInt(HashQuery.getHashQueryObject()['to']);
        if (!fromTimestamp || !toTimestamp) return;

        var pager = $('.ajax-paged').data('pager');
        pager.reset();
        pager.setProducerArgs({
            'device_id': this.deviceId,
            'from_timestamp': fromTimestamp,
            'to_timestamp': toTimestamp
        });
        pager.onAfterPaging(
            function() {
                Pager.init();
            }
        );
        pager.getPage();
        Dajaxice.apps.swid.get_tag_inventory_stats(this.updateStats, {
            'device_id': this.deviceId,
            'from_timestamp': fromTimestamp,
            'to_timestamp': toTimestamp
        },
        {'error_callback': function() {
            alert('Error: Could not fetch tag inventory stats.');
        }});
    };

    this.updateStats = function(data) {
        $('.sessionCount').text(data.session_count);
        $('.firstSession').text(data.fist_session);
        $('.lastSession').text(data.last_session);
    };
}

function setupResetButton(fromDatepicker, toDatepicker, sessionsLoader) {
    $("#session-filter-reset").click(function () {
        $("#calendar-shortcuts").prop("selectedIndex", 0);
        fromDatepicker.datepicker("setDate", new Date());
        toDatepicker.datepicker("setDate", new Date());
        setFromDateHash(fromDatepicker);
        setToDateHash(toDatepicker);
        sessionsLoader.loadSessions();
    });
}

function setupRangeShortcutsDropdown(fromDatepicker, toDatepicker, sessionsLoader) {
    $("#calendar-shortcuts").change(function () {
            fromDatepicker.datepicker("setDate", $(this).val());
            toDatepicker.datepicker("setDate", new Date());
            fromDatepicker.datepicker("option", {"maxDate": new Date()});
            toDatepicker.datepicker("option", {"minDate": $(this).val()});

            HashQuery.setHashKey({
                'from': fromDatepicker.datepicker("getDate").getTime() / 1000,
                'to': toDatepicker.datepicker("getDate").getTime() / 1000
            }, true);
            sessionsLoader.loadSessions();
        }
    );
}

function setupDatepicker(fromDatepicker, toDatepicker, sessionsLoader) {
    fromDatepicker.datepicker({
        defaultDate: new Date(),
        dateFormat: "M dd. yy",
        changeMonth: true,
        numberOfMonths: 1,
        onSelect: function (selectedDate) {
            $("#calendar-shortcuts").prop("selectedIndex", 0);
            toDatepicker.datepicker("option", {"minDate": selectedDate});
            setFromDateHash(fromDatepicker);
            sessionsLoader.loadSessions();
        }
    });

    toDatepicker.datepicker({
        defaultDate: new Date(),
        changeMonth: true,
        dateFormat: "M dd. yy",
        numberOfMonths: 1,
        onSelect: function (selectedDate) {
            $("#calendar-shortcuts").prop("selectedIndex", 0);
            fromDatepicker.datepicker("option", {"maxDate": selectedDate});
            setToDateHash(toDatepicker);
            sessionsLoader.loadSessions();
        }
    });

    var today = new Date();
    fromDatepicker.datepicker("setDate", today);
    fromDatepicker.datepicker("option", "maxDate", today);
    toDatepicker.datepicker("setDate", today);
    toDatepicker.datepicker("option", "minDate", today);

    $("#from-btn").click(function () {
        fromDatepicker.datepicker("show");
    });

    $("#to-btn").click(function () {
        toDatepicker.datepicker("show");
    });
}

function setFromDateHash(fromDatepicker) {
    var fromTimestamp = fromDatepicker.datepicker("getDate").getTime() / 1000;
    HashQuery.setHashKey({'from': fromTimestamp}, true);
}

function setToDateHash(toDatepicker) {
    var toTimestamp = toDatepicker.datepicker("getDate").getTime() / 1000;
    HashQuery.setHashKey({'to': toTimestamp}, true);
}

$(document).ready(function () {
    var fromDatepicker = $("#from");
    var toDatepicker = $("#to");

    var sessionsLoader = new AjaxSessionsLoader();
    var tagsLoader = new AjaxTagsLoader();

    // setup components
    setupDatepicker(fromDatepicker, toDatepicker, sessionsLoader);
    setupRangeShortcutsDropdown(fromDatepicker, toDatepicker, sessionsLoader);
    setupResetButton(fromDatepicker, toDatepicker, sessionsLoader);

    $('body').on('show', '#sessionAccordion', function (event) {
        var $triggeredSection = $(event.target);
        if(!$triggeredSection.data('loaded')) {
            $triggeredSection.data('loaded', true);
            var sessionId = $triggeredSection.data('sessionid');
            tagsLoader.loadTags(sessionId, $triggeredSection);
        }
    });

    HashQuery.addChangedListener('from', function () {
        sessionsLoader.loadSessions();
    });

    HashQuery.addChangedListener('to', function () {
        sessionsLoader.loadSessions();
    });

    var hashQueryObject = HashQuery.getHashQueryObject();
    if(hashQueryObject['to'] && hashQueryObject['from']) {
        var fromTimestamp = new Date(hashQueryObject['from'] * 1000);
        fromDatepicker.datepicker("setDate", fromTimestamp);
        toDatepicker.datepicker("option", {"minDate": fromTimestamp});
        var toTimestamp = new Date(hashQueryObject['to'] * 1000);
        toDatepicker.datepicker("setDate", toTimestamp);
        fromDatepicker.datepicker("option", {"maxDate": toTimestamp});
    }

    sessionsLoader.loadSessions();
});
