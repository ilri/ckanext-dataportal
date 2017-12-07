/**
 * Created by cquiros on 15/06/15.
 */

"use strict";


$(document).ready(function ()
{

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


function showAddDatasetToToken()
{
    $('#AddDatasetToToken').modal('show');
}

function showRemoveDatasetFromToken(id)
{
    document.getElementById('datasetID').value = id;
    $('#removeDataset').modal('show');
}

function showAddResourceToToken()
{
    $('#resourceTree').jstree("deselect_all");
    //$('#resourceTree').jstree.multiple = false;
    $("#resourceTree").animate({ scrollTop: 0 }, "fast");
    //$.jstree.reference('#resourceTree').deselect_all(false);
    document.getElementById('addResource').disabled = true;
    $('#AddResourceToToken').modal('show');
}

function showRemoveResourceFromToken(datasetID,resourceID)
{
    document.getElementById('removeDatasetID').value = datasetID;
    document.getElementById('removeResourceID').value = resourceID;
    $('#removeResource').modal('show');
}