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

