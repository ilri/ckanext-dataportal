/**
 * Created by cquiros on 15/06/15.
 */

"use strict";

function checkPasswordMatch() {
    var password = $("#pass1").val();
    var confirmPassword = $("#pass2").val();

    if (password == "" || confirmPassword == "")
    {
        document.getElementById('addUser').disabled = true;
        document.getElementById('addUserR').disabled = true;
    }
    if (password != confirmPassword)
    {
        document.getElementById('addUser').disabled = true;
        document.getElementById('addUserR').disabled = true;
    }
    else
    {
        if (password != "" && confirmPassword != "")
        {
            document.getElementById('addUser').disabled = false;
            document.getElementById('addUserR').disabled = false;
        }
    }
}

$(document).ready(function ()
{
    $("#pass1").keyup(checkPasswordMatch);
    $("#pass2").keyup(checkPasswordMatch);

    if (document.getElementById("datasetName"))
    {
        $("#datasetName").chosen();
    }
    if (document.getElementById("resourceTree"))
    {
        $('#resourceTree')
        // listen for event
            .on('changed.jstree', function (e, data) {
                var i, j, r = [];
                for(i = 0, j = data.selected.length; i < j; i++) {
                    r.push(data.instance.get_node(data.selected[i]).id);
                }
                if (r.length > 0) {
                    var n = r[0].indexOf("|");
                    if (n >= 0) {
                        document.getElementById('resourceID').value = r[0];
                        document.getElementById('addResource').disabled = false;
                    }
                    else
                        document.getElementById('addResource').disabled = true;
                    //$('#event_result').html('Selected: ' + r.join(', '));
                }
                else
                     document.getElementById('addResource').disabled = true;
            })
            // create the instance
            .jstree({core:{multiple : false}});
    }


});

function showAddUser()
{
    document.getElementById('id').value = "";
    document.getElementById('name').value = "";
    document.getElementById('email').value = "";
    document.getElementById('org').value = "";
    document.getElementById('pass1').value = "";
    document.getElementById('pass2').value = "";
    document.getElementById('addUser').disabled = true;
    $('#AddUser').modal('show');
}

function showModifyUser(id,name,email,org,active)
{
    document.getElementById('UPDid').value = id;
    document.getElementById('UPDname').value = name;
    document.getElementById('UPDemail').value = email;
    document.getElementById('UPDorg').value = org;
    document.getElementById('UPDpass1').value = "";
    document.getElementById('UPDpass2').value = "";

    var theForm = document.forms['formUser'];
    if (active == 1) {

        document.getElementById('UPDactive').setAttribute("checked","checked")
        $('input[id="UPDactive"]').bootstrapSwitch('state', true, true);
        //alert("True");
    }
    else {
        document.getElementById('UPDactive').removeAttribute("checked")
        $('input[id="UPDactive"]').bootstrapSwitch('state', false, true);
        //alert("False");
    }

    $('#UpdateUser').modal('show');
}

function showDeleteUser(id)
{
    document.getElementById('DELid').value = id;
    $('#DeleteUser').modal('show');
}

function showAddDatasetToUser()
{
    $('#AddDatasetToUser').modal('show');
}

function showRemoveDatasetFromUser(id)
{
    document.getElementById('datasetID').value = id;
    $('#removeDataset').modal('show');
}

function showAddResourceToUser()
{
    $('#resourceTree').jstree("deselect_all");
    //$('#resourceTree').jstree.multiple = false;
    $("#resourceTree").animate({ scrollTop: 0 }, "fast");
    //$.jstree.reference('#resourceTree').deselect_all(false);
    document.getElementById('addResource').disabled = true;
    $('#AddResourceToUser').modal('show');


}

function showRemoveResourceFromUser(datasetID,resourceID)
{
    document.getElementById('removeDatasetID').value = datasetID;
    document.getElementById('removeResourceID').value = resourceID;
    $('#removeResource').modal('show');
}