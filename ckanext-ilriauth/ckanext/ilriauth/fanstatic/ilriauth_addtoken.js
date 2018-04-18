/**
 * Created by cquiros on 15/06/15.
 */

"use strict";

$(document).ready(function ()
{
    $('#tokeList').DataTable( {
        "order": [[ 0, "desc" ]]
    } );
});

function showDeleteUser(id)
{
    document.getElementById('tokenID').value = id;
    $('#RemoveToken').modal('show');
}

function showAllocateToken(id)
{
    document.getElementById('requestID').value = id;
    $('#AllocateToken').modal('show');
}

function emailToken(id)
{
    var url = $('#' + id).val()

    $.ajax({
        type: "POST",
        url: url
    });
    alert("The email was sent.")

    // var form = document.createElement('form');
    // form.setAttribute('method', 'post');
    // form.setAttribute('action', url);
    // form.style.display = 'hidden';
    //
    // document.body.appendChild(form)
    // form.submit();
}