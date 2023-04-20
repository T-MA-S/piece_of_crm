function remove_from_board(permissions_id) {
    const csrftoken = Cookies.get('csrftoken');
    $.ajax({
        url: `/ru/crm/board/remove_from_board/${permissions_id}`,
        type: 'GET',
        headers: {"X-CSRFToken": csrftoken},
        success: function (data) {
            if (data.success) {
                location.reload();
            } else {
            }
        }
    });

}

function delete_board(board_id) {
    const csrftoken = Cookies.get('csrftoken');
    $.ajax({
        url: `/ru/crm/${board_id}/delete/`,
        type: 'DELETE',
        headers: {"X-CSRFToken": csrftoken}
    })
}

function accept_board_invite(invite_id) {
    const csrftoken = Cookies.get('csrftoken');
    $.ajax({
        url: `/ru/crm/accept_board_invite/${invite_id}/`,
        type: 'POST',
        headers: {"X-CSRFToken": csrftoken},
        success: function (data) {
            location.reload()
        }
    })
}

function decline_board_invite(invite_id) {
    const csrftoken = Cookies.get('csrftoken');
    $.ajax({
        url: `/ru/crm/decline_board_invite/${invite_id}/`,
        type: 'POST',
        headers: {"X-CSRFToken": csrftoken},
        success: function (data) {
            location.reload()
        }
    })
}

function board_event(e, id) {
    e.preventDefault();
    $(`#${id}`).modal('show')
}