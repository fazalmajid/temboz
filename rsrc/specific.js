/* get user selection, empty string if none or unsupported browser */
function get_selection() {
  var userSelection;
  userSelection = "";
  if(window.getSelection) {
    userSelection = String(window.getSelection());
  } else if (document.selection) {
    userSelection = document.selection.createRange().text;
  }
  return $.trim(userSelection);
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
