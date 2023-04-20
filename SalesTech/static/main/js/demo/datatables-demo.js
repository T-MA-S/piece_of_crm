// Call the dataTables jQuery plugin
$(document).ready(function() {
    $( ".dataTable" ).each(function() {
      $( this ).DataTable({
        "responsive": true,
        "select": true,
        "buttons": [
            {
                text: 'My button',
                className: 'vawd',
                action: function ( e, dt, node, config ) {
                    alert( 'Button activated' );
                }
            }
        ],
        "language": {
            "emptyTable": gettext("No data available in table"),
            "search": gettext("Search"),
            "lengthMenu": gettext("Show _MENU_ records"),
            "info": gettext("Shown from _START_ to _END_ (total: _TOTAL_)"),
            "paginate": {
                "first":      gettext("first"),
                "last":       gettext("last"),
                "next":       gettext("next"),
                "previous":   gettext("previous")
            },
       }
      });
      $( this ).find( 'tbody' ).on( 'click', 'tr', function () {
            $(this).toggleClass('selected');
        } );
    });
});
