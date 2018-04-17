/**
 * Created by cquiros on 15/06/15.
 */

"use strict";


$(document).ready(function ()
{
    var url;
    url = $('#statsurl').val()
    $('#stats').DataTable( {
        dom: 'Blfrtip',
        buttons: [
            'copyHtml5',
            'excelHtml5',
            'csvHtml5',
            'pdfHtml5'
        ],
        "processing": true,
        "serverSide": true,
        "scrollX": true,
        "ajax": {
            'url':url,
            'type':"POST"
        },
        "columns": [
            { "data": "request_id","name": "request_id" },
            { "data": "request_date","name": "request_date" },
            { "data": "request_ip","name": "request_ip" },
            { "data": "resource_id","name": "resource_id" },
            { "data": "resource_format","name": "resource_format" },
            { "data": "token_id","name": "token_id" },
            { "data": "user_id","name": "user_id" },
            { "data": "request_name","name": "request_name" },
            { "data": "request_email","name": "request_email" },
            { "data": "request_org","name": "request_org" },
            { "data": "request_orgtype","name": "request_orgtype" },
            { "data": "request_country","name": "request_country" },
            { "data": "request_datausage","name": "request_datausage" },
            { "data": "request_hearfrom","name": "request_hearfrom" },
        ],
        "columnDefs": [
        {"className": "dt-center", "targets": "_all"}
      ],
        "lengthMenu": [[10, 50, 100, -1], [10, 50, 100, "All"]]
    } );

});