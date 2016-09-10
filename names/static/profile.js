/**
 * Created by Kelly on 3/5/2016.
 */

$(function() {
    $('a#toggle_suggestions').on('click', function() {
      $.get( $SCRIPT_ROOT+"/_toggle_suggestions", function( data ) {
          if (data.s) {
              $("p#toggle_status").text("Currently, users can type suggestions for your name.");
              $('a#toggle_suggestions').text("Click here to allow users to select a choice from your suggested names.");
          }
          else {
              $("p#toggle_status").text("Currently, users can select a choice from your suggested names.");
              $('a#toggle_suggestions').text("Click here to allow users to type suggestions for your name.");
          }
          return false;
      });
    });

    $('a#toggle_privacy').on('click', function() {
      $.get( $SCRIPT_ROOT+"/_toggle_privacy", function( data ) {
          if (data.s) {
              $("p#current_privacy").text("Currently, only logged-in users can view your profile.");
              $('a#toggle_privacy').text("Click here to allow anonymous users to view your profile as well.");
          }
          else {
              $("p#current_privacy").text("Currently, anonymous users can view your profile.");
              $('a#toggle_privacy').text("Click here to only permit logged-in users to view your profile.");
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
