
$(document).ready(function() {
    initDateTimePicker();
    initPresetSelect();
    initResetButton();
    getTagList();
});

var initDateTimePicker = function() {
    var fromPicker = $('#from').datepicker({
        dateFormat: "dd/mm/yy",
        onClose: function (selectedDate) {
            getTagList();
        }
    });

    var toPicker = $('#to').datepicker({
        dateFormat: "dd/mm/yy",
        onClose: function (selectedDate) {
            getTagList();
        }
    });
    fromPicker.datepicker("setDate", '-1w');
    toPicker.datepicker("setDate", new Date());
};

var initPresetSelect = function() {
    $("#calendar-shortcuts").change(function () {
        $("#from").datepicker("setDate", $(this).val());
        $("#to").datepicker("setDate", new Date());
        getTagList();
    });
};

var initResetButton = function() {
    $("#filter-reset").click(function (e) {
        e.preventDefault();
        $("#calendar-shortcuts").prop("selectedIndex", 1).trigger('change');
        getTagList();
    })
};

var getTagList = function() {
    var deviceId = $('#device-id').val();
    var fromTimestamp = Math.floor($('#from').datepicker("getDate").getTime() / 1000);
    var toTimestamp = Math.floor($('#to').datepicker("getDate").getTime() / 1000);

    Dajaxice.apps.swid.get_tag_log(updateTable, {
        'device_id': deviceId,
        'from_timestamp': fromTimestamp,
        'to_timestamp': toTimestamp
    });
};

var updateTable = function (data) {
    var $noEntryText = $('#noEntryText');
    var $table = $('#swid-tags');
    var $tableBody = $table.find("tbody");

    var addedCount = 0;
    var removedCount = 0;
    var sessionCount = 0;
    var firstSession = 'None';
    var lastSession = 'None';

    $tableBody.empty();

    var rows = document.createDocumentFragment();

    if(data.length == 0){
        $table.hide();
        $noEntryText.show();
    } else {
        $noEntryText.hide();
        $table.show();
        $.each(data, function (i, record) {
            var hasSessionLead = false;
            $.each(record['added_tags'], function (i, tag) {
                var tr = $("<tr></tr>");
                if (i == 0) {
                    tr = addSessionCell(tr, record);
                    hasSessionLead = true;
                }
                tr = addTagRow(tr, tag, 'ADDED');
                tr.appendTo(rows);
            });
            $.each(record['removed_tags'], function (i, tag) {
                var tr = $("<tr></tr>");
                if (!hasSessionLead && i == 0) {
                    tr = addSessionCell(tr, record);
                }
                tr = addTagRow(tr, tag, 'REMOVED');
                tr.appendTo(rows);
            });
            addedCount += record['added_tags'].length;
            removedCount += record['removed_tags'].length;
        });
        firstSession = data.shift()['session_date'];
        lastSession = data.pop()['session_date'];
        sessionCount = data.length;
        $tableBody.append(rows);
    }
    updateStats(addedCount, removedCount, sessionCount, firstSession, lastSession);
};

var addTagRow = function(tr, tag, type) {
    tr.append($("<td></td>").html(type));
    var tagLink = $('<a/>', {
        href: '/swid-tags/' + tag['tag_id'],
        text: tag['unique_id']
    });
    tr.append($("<td></td>").append(tagLink));
    return tr;
};

var addSessionCell = function(tr, record) {
    var sessionLink = $('<a/>', {
        href: '/sessions/' + record['session_id'],
        text: record['session_date']
    });
    tr.append($("<td></td>").attr('rowspan', record['tag_count']).append(sessionLink));
    return tr;
};

var updateStats = function(addedCount, removedCount, sessionCount, firstSession, lastSession) {
    var $statsTable = $('.statsTable');
    $('.sessionCount', $statsTable).text(sessionCount);
    $('.addedTags', $statsTable).text(addedCount);
    $('.removedTags', $statsTable).text(removedCount);
    $('.firstSession', $statsTable).text(firstSession);
    $('.lastSession', $statsTable).text(lastSession);
};