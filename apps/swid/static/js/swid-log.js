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

    $("#from-btn").click(function () {
        fromPicker.datepicker("show");
    });

    $("#to-btn").click(function () {
        toPicker.datepicker("show");
    });
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

    var pager = $('.ajax-paged', '#logTabelContainer').data('pager');
    pager.reset();
    pager.setProducerArgs({
        'device_id': deviceId,
        'from_timestamp': fromTimestamp,
        'to_timestamp': toTimestamp
    });
    pager.getPage();

    Dajaxice.apps.swid.get_tag_log_stats(updateStats, {
        'device_id': deviceId,
        'from_timestamp': fromTimestamp,
        'to_timestamp': toTimestamp
    }, {'error_callback': function() {
        alert('Error: Could not fetch tag log stats.');
    }});
};

var updateStats = function(data) {
    var $statsTable = $('.statsTable');
    $('.sessionCount', $statsTable).text(data['session_count']);
    $('.addedTags', $statsTable).text(data['added_count']);
    $('.removedTags', $statsTable).text(data['removed_count']);
    $('.firstSession', $statsTable).text(data['first_session']);
    $('.lastSession', $statsTable).text(data['last_session']);
};
