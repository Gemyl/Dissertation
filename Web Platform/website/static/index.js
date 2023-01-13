$(".is").click(function(event) {
    var radio_selector = 'input[type="radio"]',
        $radio;

    // Ignore the event when the radio input is clicked.
    if (!$(event.target).is(radio_selector)) {
        $radio = $(this).find(radio_selector);
        // Prevent the event to be triggered
        // on another element, for the same click
        event.stopImmediatePropagation();
        // We manually check the box, so prevent default
        event.preventDefault();
        $radio.prop('checked', !$radio.is(':checked'));
    }
});
$(".il-radio").on('change click', function(event) {
    // The change event only fires when the checkbox state changes
    // The click event always fires
    
    // When the radio is already checked, this event will fire only once,
    // resulting in an unchecked checkbox.
    // When the radio is not checked already, this event fires twice
    // so that the state does not change
    this.checked = !this.checked;
})
