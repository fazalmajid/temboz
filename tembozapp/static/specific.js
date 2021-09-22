// get user selection, empty string if none or unsupported browser
// on Safari iOS clicking on a UI element like the "thumbs up" arrow
// deselects, so we save the selection as soon as it is completed in
// a global variable
var saved_selection = "";

function raw_selection() {
    var userSelection;
    userSelection = "";
    if(window.getSelection) {
        userSelection = String(window.getSelection());
    } else if (document.selection) {
        userSelection = document.selection.createRange().text;
    }
    return $.trim(userSelection);
}
function save_selection() {
    saved_selection = raw_selection();
}
function get_selection() {
    var s = raw_selection();
    if (s == "" && saved_selection != "") s = saved_selection;
    return s;
}

function capitalize(s) {
    return s.charAt(0).toUpperCase() + s.substring(1);
}
/* pop-up menus */
function place_popup() {
    var popup = $("div#popup_" + this.id);
    this.popup = popup;
}
function hide_popups() {
    $(document).unbind("click", hide_popups);
    $("div.popup").hide();
}
function show_popup(event) {
    event.stopPropagation();

    var callout = $(this).offset();
    var container = $(this).offsetParent().offset();
    this.popup.css("left", callout.left - container.left);
    this.popup.css("top", callout.top - container.top + $(this).height() + 3);

    this.popup.toggle();
    $(document).click(hide_popups);
}
function init_popups() {
    $(document).ready(function() {
        $("a.callout").each(place_popup);
        $("a.callout").click(show_popup);
    });
}
function rand() {
    return Math.random().toString().substring(8);
}
/* work around jQuery bug */
$.widget( "ui.tabs", $.ui.tabs, {
    _isLocal: function( anchor ) {
        // If there's no hash, it can't be local
        if ( !anchor.hash.length ) {
            return false;
        }

        // http://bugs.jqueryui.com/ticket/11223
        // Intentionally skip hash, username, password
        // href may contain username and password, so we can't use that
        // host, hostname, port, and protocol are all included in origin
        var urlParts = [ "origin", "pathname", "search" ];
        var isLocal = true;

        $.each( urlParts, function( urlPart ) {
            var anchorValue = anchor[ urlPart ];
            var locationValue = location[ urlPart ];

            // Decoding may throw an error if the URL isn't UTF-8 (#9518)
            try {
	        anchorValue = decodeURIComponent( anchorValue );
            } catch ( error ) {}
            try {
	        locationValue = decodeURIComponent( locationValue );
            } catch ( error ) {}

            if ( anchorValue !== locationValue ) {
	        isLocal = false;
	        return false;
            }
        });

        return isLocal;
    }
});
/* search */
$(function() {
    $("input#search").focus(
        function() {
            $("select.hidden").show();
        }
    );
    document.body.addEventListener("touchend", function(e) {
        save_selection();
    }, false);
});
