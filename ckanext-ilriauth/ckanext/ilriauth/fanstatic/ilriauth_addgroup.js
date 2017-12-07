/**
 * Created by cquiros on 15/06/15.
 */

"use strict";


$(document).ready(function ()
{

    if (document.getElementById("userID"))
    {
        $("#userID").chosen();
    }

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

function showAddGroup()
{
    document.getElementById('name').value = "";
    $('#AddGroup').modal('show');
}

function showModifyGroup(id,name)
{
    document.getElementById('UPDid').value = id;
    document.getElementById('UPDname').value = name;

    $('#UpdateGroup').modal('show');
}

function showDeleteGroup(id)
{
    document.getElementById('DELid').value = id;
    $('#DeleteGroup').modal('show');
}

function showAddUserToGroup()
{
    $('#AddUserToGroup').modal('show');
}

function showRemoveMemberFromGroup(id)
{
    document.getElementById('memberID').value = id;
    $('#removeUser').modal('show');
}

function showAddDatasetToGroup()
{
    $('#AddDatasetToGroup').modal('show');
}

function showRemoveDatasetFromGroup(id)
{
    document.getElementById('datasetID').value = id;
    $('#removeDataset').modal('show');
}

function showAddResourceToGroup()
{
    $('#resourceTree').jstree("deselect_all");
    //$('#resourceTree').jstree.multiple = false;
    $("#resourceTree").animate({ scrollTop: 0 }, "fast");
    //$.jstree.reference('#resourceTree').deselect_all(false);
    document.getElementById('addResource').disabled = true;
    $('#AddResourceToGroup').modal('show');
}

function showRemoveResourceFromGroup(datasetID,resourceID)
{
    document.getElementById('removeDatasetID').value = datasetID;
    document.getElementById('removeResourceID').value = resourceID;
    $('#removeResource').modal('show');
}