// $( "#restorePassForm" ).submit(function( event ) {

//   // Stop form from submitting normally
//   event.preventDefault();

//   // Get some values from elements on the page:
//   var $form = $( this ),
//     url = $form[0].action;

//   // Send the data using post
//   var posting = $.post( url, $form.serialize() );

//   // Put the results in a div
//   posting.done(function( data ) {
//     var text = "";
//     var title = "";
//     var warning = $( data ).find( ".warning" ).text().trim();
//     if (warning.length > 0) {
//       text = warning
//       title = gettext("Warning")
//     } else {
//       text = data
//       title = gettext("Success")
//       $( "#closeModalBtn" ).click(function() {
//           window.location.href="/"
//         });
//     }
//     $( "#resultModalTitle" ).text(title)
//     $( "#resultModalLabel" ).text(text)
//     $( "#resultModal" ).modal('show');
//   });

// });