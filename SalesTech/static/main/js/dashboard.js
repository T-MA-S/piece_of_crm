function accept_team_invite(invite_id) {
    const csrftoken = Cookies.get('csrftoken');
    $.ajax({
        url: `/ru/accept_invite/${invite_id}`,
        type: 'GET',
        headers: {"X-CSRFToken": csrftoken},
        success: function (data) {
            if (data.success) {
                location.reload();
            } else {
            }
        }
    });
    window.location.reload()
}

function reject_team_invite(invite_id) {
    const csrftoken = Cookies.get('csrftoken');
    $.ajax({
        url: `/ru/reject_invite/${invite_id}`,
        type: 'GET',
        headers: {"X-CSRFToken": csrftoken},
        success: function (data) {
            if (data.success) {
                location.reload();
            } else {
            }
        }
    });
    window.location.reload()
}

function remove_from_team(user_id) {
    const csrftoken = Cookies.get('csrftoken');
    $.ajax({
        url: `/ru/team/remove_from_team/${user_id}`,
        type: 'GET',
        headers: {"X-CSRFToken": csrftoken},
        success: function (data) {
            if (data.success) {
                location.reload();
            } else {
            }
        }
    });
    window.location.reload()
}