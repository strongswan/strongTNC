/**
 * Common JavaScript functions that can be used on every page.
 *
 * Note that this script is loaded in the footer, so always wait for the
 * document ready event before accessing the DOM.
 */

/**
 * Link tags with the "history_back" function trigger "window.history.back()".
 */
$('body').on('click', 'a.history_back', function(event) {
    event.preventDefault();
    history.back();
});
