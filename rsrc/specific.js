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
  var callout_pos = $(this).position();
  popup.css("left", callout_pos.left);
  popup.css("top", callout_pos.top + $(this).height() + 3);
  this.popup = popup;
}
function hide_popups() {
  $(document).unbind("click", hide_popups);
  $("div.popup").hide();
}
function show_popup(event) {
  event.stopPropagation();
  this.popup.toggle();
  $(document).click(hide_popups);
}
