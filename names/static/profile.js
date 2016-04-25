/**
 * Created by Kelly on 3/5/2016.
 */

$(function() {
    $('a#toggle_suggestions').on('click', function() {
      $.get( $SCRIPT_ROOT+"/_toggle_suggestions", function( data ) {
          if (data.s) {
              $("p#toggle_status").text("Currently, logged-in users can type suggestions for your name.");
              $('a#toggle_suggestions').text("Click here to allow users and guests to select a choice from your suggested names.");
          }
          else {
              $("p#toggle_status").text("Currently, users and guests can select a choice from your suggested names.");
              $('a#toggle_suggestions').text("Click here to allow logged-in users to type suggestions for your name.");
          }
          return false;
      });
    });

    $('.delete').on('click', function() {
        $.get( $SCRIPT_ROOT+"/_"+this.id, function(data) {
            $("#"+ data.id).text("Name deleted.");
          return false;
      });
    });

    $('.report').on('click', function() {
        $.get( $SCRIPT_ROOT+"/_"+this.id, function(data) {
            if (data.active) {
                $("#"+ data.id).text("Name reported.");
            } else {
                $("#"+ data.id).text("An anonymous user suggested this name so it could not be reported. I'm working on a solution.");
            }
          return false;
      });
    });
});
