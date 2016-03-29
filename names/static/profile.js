/**
 * Created by Kelly on 3/5/2016.
 */

$(function() {
    $('a#toggle_suggestions').bind('click', function() {
      $.get( $SCRIPT_ROOT+"/_toggle_suggestions", function( data ) {
          if (data.s) {
              $("p#toggle_status").text("Currently, logged-in users can type suggestions for your name.");
              $('a#toggle_suggestions').text("Click here to allow users and guests to select a choice from your suggested names.");
          }
          else {
              $("p#toggle_status").text("Currently, users and guests can select a choice from your suggested names.");
              $('a#toggle_suggestions').text("Click here to allow logged-in users to type suggestions for your name.");
          }
          alert( "You changed stuff." );
          return false;
      });
    });
});