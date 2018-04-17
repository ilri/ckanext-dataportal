// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
"use strict";

var activityMap;
var boundBoxLayer;
var mapLoaded = false;
var mapControl;
var countryTags;
var crpTags;
var regionsTags;
var speciesTags;
var subjectsTags;
var mainTags;

var actySpeciesTags;
var actyRegionsTags;
var actyCountriesTags;
var actyNatLevelTags;

function getTagList(url_address)
{
    var CRPArray = new Array();

    $.ajax(
        {
            url: url_address,
            dataType: 'json',
            async: false,  //False so we use it in tags. Othewise we would need to embed tag in a success function.
            success: function(data) {
                $.each( data, function( key, val )
                {
                    CRPArray.push(val);
                });
            }
        });
    return CRPArray;
};

//This function copy the Dataset metadata from a source dataset
function copyStudyData()
{
    var seldataset = $( "#sourceStudy" ).val();
    if (seldataset !== "None")
    {
        $.getJSON( "/portal/api/3/action/package_show?id=" + seldataset, function( data ) {
            $('#field-notes').val(data["result"].notes);
            $.each( data["result"], function( key, val ) {
                var value = val;
                var sub = key.substring(0,8);
                if ((sub == "ILRI_act") || (key == "ILRI_prjsubjects"))
                {
                    if ((key != "ILRI_actynatlevel") && (key != "ILRI_actyregions") && (key != "ILRI_actycountries") && (key != "ILRI_prjsubjects") && (key != "ILRI_actyspecies"))
                        $('#'+key).val(value);
                    else
                    {
                        var myArray;
                        if (key == "ILRI_actynatlevel")
                        {
                            myArray = value.split(",");
                            for (var i in myArray) {
                                actyNatLevelTags.tagsManager("pushTag", myArray[i]);
                            }
                        }
                        if (key == "ILRI_actyregions")
                        {
                            myArray = value;
                            for (var i in myArray) {
                                actyRegionsTags.tagsManager("pushTag", myArray[i]);
                            }
                        }
                        if (key == "ILRI_actycountries")
                        {
                            myArray = value;
                            for (var i in myArray) {
                                actyCountriesTags.tagsManager("pushTag", myArray[i]);
                            }
                        }
                        if (key == "ILRI_prjsubjects")
                        {
                            myArray = value;
                            for (var i in myArray) {
                                subjectsTags.tagsManager("pushTag", myArray[i]);
                            }
                        }
                        if (key == "ILRI_actyspecies")
                        {
                            myArray = value;
                            for (var i in myArray) {
                                actySpeciesTags.tagsManager("pushTag", myArray[i]);
                            }
                        }
                    }
                }
            });
            $.each( data['result']["tags"], function( row ) {
                var key = data['result']["tags"][row]["vocabulary_id"];
                var value = data['result']["tags"][row]["name"];
                if (key == null)
                {
                    mainTags.tagsManager("pushTag",value);
                }
            });


        });

    }
};

//This function copy the project data from a source dataset
function copyProjectData()
{
    var seldataset = $( "#sourceProject" ).val();
    if (seldataset != "None")
    {
        $.getJSON( "/portal/api/3/action/package_show?id=" + seldataset, function( data ) {
            $.each( data['result'], function( key,value ) {
                var sub = key.substring(0,8);
                if (sub == "ILRI_prj")
                {
                    if ((key != "ILRI_prjcountries") && (key != "ILRI_prjregions") && (key != "ILRI_prjspecies"))
                        $('#'+key).val(value);
                    else
                    {
                        var myArray;
                        if (key == "ILRI_prjcountries")
                        {
                            myArray = value.split("+");
                            for (var i in myArray)
                            {
                                countryTags.tagsManager("pushTag", myArray[i]);
                            }
                        }
                        if (key == "ILRI_prjregions")
                        {
                            myArray = value.split(",");
                            for (var i in myArray)
                            {
                                regionsTags.tagsManager("pushTag", myArray[i]);
                            }
                        }
                        if (key == "ILRI_prjspecies")
                        {
                            myArray = value.split(",");
                            for (var i in myArray) {
                                speciesTags.tagsManager("pushTag", myArray[i]);
                            }
                        }
                    }
                }
            });


        });
    }
}


function cleaMapArea()
{
    if (boundBoxLayer)
    {
        activityMap.removeLayer(boundBoxLayer);
    }
}

function getCoordinates()
{
    vex.dialog.open({
        message: 'Enter the coordinates of the area in degrees:',
        input: "<input name=\"southWestLat\" type=\"text\" placeholder=\"South-West Latitude (Lower Right Y)\" required />\n<input name=\"southWestLong\" type=\"text\" placeholder=\"South-West Longitude (Lower Right X)\" required />\n<input name=\"northEastLat\" type=\"text\" placeholder=\"Nnorth-East Latitude (Upper Left Y)\" required />\n<input name=\"northEastLong\" type=\"text\" placeholder=\"Nnorth-East Longitude (Upper Left X)\" required />",
        buttons: [
            $.extend({}, vex.dialog.buttons.YES, {
                text: 'Accept'
            }), $.extend({}, vex.dialog.buttons.NO, {
                text: 'Cancel'
            })
        ],
        callback: function(data) {

            if (data != false)
            {
                if (boundBoxLayer)
                {
                    activityMap.removeLayer(boundBoxLayer);
                }

                var value;
                var mapExtent = { southWestLat: 0, southWestLong: 0, northEastLat: 0,  northEastLong: 0};

                mapExtent['southWestLat'] = parseFloat(data.southWestLat);
                mapExtent['southWestLong'] = parseFloat(data.southWestLong);
                mapExtent['northEastLat'] = parseFloat(data.northEastLat);
                mapExtent['northEastLong'] = parseFloat(data.northEastLong);

                value = $.toJSON( mapExtent );
                //Set the value to the HTML input
                $('#ILRI_actyboundbox').val(value);
                $('#ILRI_actymapextent').val(value);

                var southWest;
                var northEast;
                var bounds;

                southWest = L.latLng(parseFloat(data.southWestLat),parseFloat(data.southWestLong));
                northEast = L.latLng(parseFloat(data.northEastLat),parseFloat(data.northEastLong));
                bounds = L.latLngBounds(southWest, northEast);

                $('#ILRI_actyboundboxcenter').val(bounds.getCenter().lat + "," + bounds.getCenter().lng);

                activityMap.fitBounds(bounds);


                boundBoxLayer = L.rectangle(bounds);
                activityMap.addLayer(boundBoxLayer);

                $('#ILRI_actymapzoom').val(activityMap.getZoom());

            }
        }
    });
}

function generateCitation()
{
    var pi = document.getElementById("ILRI_actypi").value;
    var others = document.getElementById("ILRI_actystaff").value;
    var strdate = (document.getElementById("ILRI_actydatavailable").value);
    var arrdate = strdate.split("/");
    var avadate = new Date(arrdate[2]+"-"+arrdate[1]+"-"+arrdate[0]);
    var year = avadate.getFullYear();
    var title = document.getElementById("field-title").value;
    var owner = document.getElementById("ILRI_actyipownership").value;

    if (pi == "") pi = "Principal investigator is empty!";
    if (title == "") title = "Title is empty!";
    if (owner == "") owner = "Intellectual Property Ownership is empty!";
    if (others != "") others = ", " + others;

    var name;
    if (document.getElementById("field-name"))
        name = document.getElementById("field-name").value;
    else {
        if (document.getElementById("dataset-name"))
            name = document.getElementById("dataset-name").value;
    }

    var citation = pi + others + " (" + year.toString() + "). " + title + ". " + owner;
    citation = citation + ". Available at http://data.ilir.org/dataset/" + name + ", retrieved on (add date here)";
    //alert(citation)
    document.getElementById("ILRI_actycitation").value = citation;
}

function loadConfFields(APIUrl)
{
    var resourceURL = document.getElementById("field-image-url").value;
    var currentContent = document.getElementById("resource_description").value;
    if (resourceURL != "")
    {
        if (resourceURL.indexOf("getdata") > -1)
        {
            var n = resourceURL.lastIndexOf("/");
            if (n > -1)
            {
                var dataset = resourceURL.substr(n+1,resourceURL.length-n-1);
                var JSONURL = APIUrl + "?id=" + dataset;
                currentContent = currentContent + "\n#### The following fields are confidential in this dataset";
                var tableDesc = "";
                $.getJSON( JSONURL, function( data )
                {
                    data.forEach(function(object)
                    {
                        if (tableDesc != object.tbldesc)
                        {
                            tableDesc = object.tbldesc;
                            currentContent = currentContent + "\n\nTable: " + object.tblname + " (" + object.tbldesc +")\n\n";
                        }
                        currentContent = currentContent + "- " + object.clmname + " (" + object.clmdesc + ")\n";
                    });
                    document.getElementById("resource_description").value = currentContent;
                });
            }
            else
            {
                currentContent = currentContent + "\n#### The following fields are confidential in this dataset\nAdd them manually";
                document.getElementById("resource_description").value = currentContent;
            }
        }
        else
        {
            currentContent = currentContent + "\n#### The following fields are confidential in this dataset\nAdd them manually";
            document.getElementById("resource_description").value = currentContent;
        }
    }
    else
    {
        currentContent = currentContent + "\n#### The following fields are confidential in this dataset\nAdd them manually";
        document.getElementById("resource_description").value = currentContent;
    }
}

//This function toggle the access between public and confidential in GetData resources
function toggleAccess(resource_id,imageURL)
{
    var image;
    image = imageURL;
    $('#' + resource_id + ' a').each(function ()
    {
        var $this = $(this),
            href = $this.attr('href');

        if ($('#confaccess').val() == "0")
        {
            if (href.indexOf("outputFormat") == -1)
                $this.attr('href', href + "?confidential=true");
            else
                $this.attr('href', href + "&confidential=true");
        }
        else
        {
            if (href.indexOf("outputFormat") == -1)
                $this.attr('href', href.replace("?confidential=true",""));
            else
                $this.attr('href', href.replace("&confidential=true",""));
        }
    });
    if ($('#confaccess').val() == "0")
    {
        $('#confaccess').val("1");
        image = image.replace("lock-gray","lock-red");
        document.getElementById("confimage").src=image;
        document.getElementById("confimage").title="Confidential access - Click to change to Public access";
    }
    else
    {
        $('#confaccess').val("0");
        image = image.replace("lock-red","lock-gay");
        document.getElementById("confimage").src=image;
        document.getElementById("confimage").title="Public access - Click to change to Confidential access";
    }
};

// This fuction converts the information of the resource form into a JSON and stores it into the resource description
// This allow is to customize the Resource form
$('.dataset-resource-form').submit(function() {

    var resource_des;
    var resource_access;
    var value;

    resource_des = $('#resource_description').val();
    resource_des = resource_des.replace('"',"'");
    resource_access = $('#ILRIResourceAccess').val();


    var dict = {'resource_description': resource_des, 'resource_access': resource_access};

    value = $.toJSON( dict );
    //Set the value to the HTML input

    $('#field-description').val(value);


});

// This function load a GetData request after page load so we can tell the user that we are processing its request and might take time or redirect to error
// User by request_info.html
$('#GetData').ready(function() {

    if (document.getElementById("GetData"))
    {
        var getDataURL = $("#resource_url").val();
        var getDataRequestData = $("#request_data").val();

        getDataURL = getDataURL + "?data=" + getDataRequestData
        //window.location.href = getDataURL;

        var hiddenIFrameID = 'hiddenDownloader',
            iframe = document.getElementById(hiddenIFrameID);
        if (iframe === null) {
            iframe = document.createElement('iframe');
            iframe.id = hiddenIFrameID;
            iframe.style.display = 'none';
            document.body.appendChild(iframe);
        }
        iframe.src = getDataURL;

    }

});

$(function()
{

    vex.defaultOptions.className = 'vex-theme-os';

    //The following function add JavaScript UI widgets to HTML items
    if (document.getElementById("sourceStudy"))
    {
        $("#sourceStudy").chosen();
    }

    if (document.getElementById("field-organizations"))
    {
        $("#field-organizations").chosen();
    }

    if (document.getElementById("ILRI_actyproduct"))
    {
        $("#ILRI_actyproduct").chosen();
    }

    if (document.getElementById("sourceProject"))
    {
        $("#sourceProject").chosen();
    }

    if (document.getElementById("field-license"))
    {
        $("#field-license").chosen();
    }

    if (document.getElementById("field_country"))
    {
        $("#field_country").chosen();
    }

    if (document.getElementById("analysistab"))
    {
        $( "#analysistab" ).tabs();
    }

    if (document.getElementById("studyMap"))
    {
        activityMap = L.map('studyMap').setView([51.505, -0.09], 13);
    }

    if (document.getElementById("ILRI_prjsdate"))
    {
        $( "#ILRI_prjsdate" ).datepicker({ dateFormat: "dd/mm/yy", changeYear: true});
        $( "#ILRI_prjedate" ).datepicker({ dateFormat: "dd/mm/yy", changeYear: true});
    }

    if (document.getElementById("ILRI_actydatecollected"))
    {
        $( "#ILRI_actydatecollected" ).datepicker({ dateFormat: "dd/mm/yy", changeYear: true});
        $( "#ILRI_actydatecollectedend" ).datepicker({ dateFormat: "dd/mm/yy", changeYear: true});
        $( "#ILRI_actydatavailable" ).datepicker({ dateFormat: "dd/mm/yy", changeYear: true});

        $( "#ILRI_actyrelconfdata" ).bootstrapSwitch();
        $( "#ILRI_actyfarmconsent" ).bootstrapSwitch();
    }

    if (document.getElementById("ILRIMetaAccordion"))
    {
        $( "#ILRIMetaAccordion" ).accordion({collapsible: true});

        //If there is a study map then add the map controls
        if (document.getElementById("studyMap"))
        {
            var active = $( "#ILRIMetaAccordion" ).accordion( "option", "active" );

            if (active == 0)
            {

                if (mapLoaded == false)
                {
                    mapLoaded = true;
                    if (mapControl)
                    {
                        activityMap.removeControl(mapControl);
                    }

                    ;	      activityMap.invalidateSize(true); //This will repaint the map once the user clicks on the tab "Study location"

                    var value;

                    var southWest;
                    var northEast;
                    var bounds;
                    var zoom;

                    //Retrive the extent of the map and set it up.
                    value = $('#ILRI_actymapextent').val();
                    if (value != "")
                    {
                        mapLoaded = true;
                        southWest = L.latLng($.evalJSON( value ).southWestLat, $.evalJSON( value ).southWestLong);
                        northEast = L.latLng($.evalJSON( value ).northEastLat, $.evalJSON( value ).northEastLong);
                        bounds = L.latLngBounds(southWest, northEast);

                        zoom = $('#ILRI_actymapzoom').val();

                        activityMap.fitBounds(bounds);
                        activityMap.setZoom(zoom);
                    }
                    //Retrive the box and add it to the map


                    value = $('#ILRI_actyboundbox').val();
                    if (value != "")
                    {

                        mapLoaded = true;
                        southWest = L.latLng($.evalJSON( value ).southWestLat, $.evalJSON( value ).southWestLong);
                        northEast = L.latLng($.evalJSON( value ).northEastLat, $.evalJSON( value ).northEastLong);
                        bounds = L.latLngBounds(southWest, northEast);

                        boundBoxLayer = L.rectangle(bounds);
                        activityMap.addLayer(boundBoxLayer);

                    }
                }
            }
        }



    };

    //Tabs in the display of the dataset
    if (document.getElementById("datasettabs"))
    {
        $( "#datasettabs" ).tabs();
    }


    if (document.getElementById("metadatatabs"))
    {

        //Tabs in #metadatatabs integrate some bits of the map in the activate function.
        //This to avoid a bug in the creation of the map control inside a Jquery Tab
        $( "#metadatatabs" ).tabs({
            activate: function( event, ui ) {

                if (document.getElementById("studyMap"))
                {

                    if (mapLoaded == false)
                    {

                        if (ui.newTab.text() == "Location")
                        {

                            activityMap.invalidateSize(true); //This will repaint the map once the user clicks on the tab "Study location"

                            var value;

                            var southWest;
                            var northEast;
                            var bounds;
                            var zoom;

                            //Retrive the extent of the map and set it up.
                            value = $('#ILRI_actymapextent').val();
                            if (value != "")
                            {
                                mapLoaded = true;
                                southWest = L.latLng($.evalJSON( value ).southWestLat, $.evalJSON( value ).southWestLong);
                                northEast = L.latLng($.evalJSON( value ).northEastLat, $.evalJSON( value ).northEastLong);
                                bounds = L.latLngBounds(southWest, northEast);

                                zoom = $('#ILRI_actymapzoom').val();

                                activityMap.fitBounds(bounds);
                                activityMap.setZoom(zoom);
                            }
                            //Retrive the box and add it to the map

                            value = $('#ILRI_actyboundbox').val();
                            if (value != "")
                            {
                                mapLoaded = true;
                                southWest = L.latLng($.evalJSON( value ).southWestLat, $.evalJSON( value ).southWestLong);
                                northEast = L.latLng($.evalJSON( value ).northEastLat, $.evalJSON( value ).northEastLong);
                                bounds = L.latLngBounds(southWest, northEast);

                                boundBoxLayer = L.rectangle(bounds);
                                activityMap.addLayer(boundBoxLayer);
                            }
                        }
                    }
                }
            }});
    }

    if (document.getElementById("studyMap"))
    {

        //Loads the base map from osm.org
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(activityMap);


        //Do not show the controls if not in edit page
        if (!document.getElementById("ILRIMetaAccordion"))
        {
            //Add the Rectangle Control to the map
            mapControl = new L.Control.Draw({
                position: 'topright',
                polyline: false, polygon: false,
                circle: false, marker: false,
                rectangle: {
                    title: 'Draw rectangle'
                }
            });
            activityMap.addControl(mapControl);

            //Tracks the rectangle-created event so we add the box to the map and save its dimentions to the forms
            activityMap.on('draw:rectangle-created', function (e) {
                if (boundBoxLayer) {
                    activityMap.removeLayer(boundBoxLayer);
                }
                boundBoxLayer = e.rect;

                var bounds;
                var southWest;
                var northEast;
                var mapExtent = { southWestLat: 0, southWestLong: 0, northEastLat: 0,  northEastLong: 0};
                var value;

                //Get the extent of the map
                bounds = activityMap.getBounds();
                southWest = bounds.getSouthWest();
                northEast = bounds.getNorthEast();
                mapExtent['southWestLat'] = southWest.lat;
                mapExtent['southWestLong'] = southWest.lng;
                mapExtent['northEastLat'] = northEast.lat;
                mapExtent['northEastLong'] = northEast.lng;

                value = $.toJSON( mapExtent );
                $('#ILRI_actymapextent').val(value);
                $('#ILRI_actymapzoom').val(activityMap.getZoom());

                //Get the extent of the box
                bounds = boundBoxLayer.getBounds();
                southWest = bounds.getSouthWest();
                northEast = bounds.getNorthEast();
                mapExtent['southWestLat'] = southWest.lat;
                mapExtent['southWestLong'] = southWest.lng;
                mapExtent['northEastLat'] = northEast.lat;
                mapExtent['northEastLong'] = northEast.lng;
                value = $.toJSON( mapExtent );
                //Set the value to the HTML input
                $('#ILRI_actyboundbox').val(value);
                $('#ILRI_actyboundboxcenter').val(bounds.getCenter().lat + "," + bounds.getCenter().lng);


                activityMap.addLayer(boundBoxLayer);
            });
        }



    }

    //Activity level tags

    //Species
    if (document.getElementById("ILRI_actyspecies"))
    {
        actySpeciesTags = jQuery(".tm-ILRI_actyspecies").tagsManager({
            output: '#ILRI_actyspecies',
            onlyTagList: true,
            tagList: getTagList("/portal/api/ilri/1/action/list_species"),
            tagsContainer: '#cnt-ILRI_actyspecies'
        });

        jQuery(".tm-ILRI_actyspecies").typeahead({
            name: 'ActySpecies',
            limit: 5,
            prefetch: '/portal/api/ilri/1/action/list_species'
        }).on('typeahead:selected', function (e, d) {
            actySpeciesTags.tagsManager("pushTag", d.value);
        });
    }

    //Regions
    if (document.getElementById("ILRI_actyregions"))
    {
        actyRegionsTags = jQuery(".tm-ILRI_actyregions").tagsManager({
                output: '#ILRI_actyregions',
                onlyTagList: true,
                tagList: getTagList("/portal/api/ilri/1/action/list_regions"),
                tagsContainer: '#cnt-ILRI_actyregions'
            }
        );

        jQuery(".tm-ILRI_actyregions").typeahead({
            name: 'ActyRegions',
            limit: 5,
            prefetch: '/portal/api/ilri/1/action/list_regions'
        }).on('typeahead:selected', function (e, d) {

            actyRegionsTags.tagsManager("pushTag", d.value);
        });
    }

    //Countries
    if (document.getElementById("ILRI_actycountries"))
    {

        actyCountriesTags = jQuery(".tm-ILRI_actycountries").tagsManager({
                output: '#ILRI_actycountries',
                onlyTagList: true,
                delimiters: [43],
                tagList: getTagList("/portal/api/ilri/1/action/list_countries"),
                tagsContainer: '#cnt-ILRI_actycountries'
            }
        );

        jQuery(".tm-ILRI_actycountries").typeahead({
            name: 'ActyCountries',
            limit: 5,
            prefetch: '/portal/api/ilri/1/action/list_countries'
        }).on('typeahead:selected', function (e, d) {

            actyCountriesTags.tagsManager("pushTag", d.value);
        });
    }

    if (document.getElementById("ILRI_actynatlevel"))
    {
        actyNatLevelTags = jQuery(".tm-ILRI_actynatlevel").tagsManager({
                output: '#ILRI_actynatlevel',
                tagsContainer: '#cnt-ILRI_actynatlevel'
            }
        );
    }

    //Subjects
    if (document.getElementById("ILRI_prjsubjects"))
    {

        subjectsTags = jQuery(".tm-ILRI_prjsubjects").tagsManager({
                output: '#ILRI_prjsubjects',
                onlyTagList: true,
                tagList: getTagList("/portal/api/ilri/1/action/list_subjects"),
                tagsContainer: '#cnt-ILRI_prjsubjects'
            }
        );

        jQuery(".tm-ILRI_prjsubjects").typeahead({
            name: 'Subjects',
            limit: 5,
            prefetch: '/portal/api/ilri/1/action/list_subjects'
        }).on('typeahead:selected', function (e, d) {

            subjectsTags.tagsManager("pushTag", d.value);

        });
    }

    //Main tags
    if (document.getElementById("field-tags"))
    {
        mainTags = jQuery(".tm-tag_string").tagsManager({
                output: '#field-tags',
                tagsContainer: '#cnt-tag_string'
            }
        );

        jQuery(".tm-tag_string").typeahead({
            name: 'mainTags',
            limit: 5,
            prefetch: '/portal/api/ilri/1/action/list_tags'
        }).on('typeahead:selected', function (e, d) {

            mainTags.tagsManager("pushTag", d.value);

        });
    }

    //Project level tags
    if (document.getElementById("ILRI_prjregions"))
    {
        //Regions
        regionsTags = jQuery(".tm-ILRI_prjregions").tagsManager({
                output: '#ILRI_prjregions',
                onlyTagList: true,
                tagList: getTagList("/portal/api/ilri/1/action/list_regions"),
                tagsContainer: '#cnt-ILRI_prjregions',
            }
        );

        jQuery(".tm-ILRI_prjregions").typeahead({
            name: 'Regions',
            limit: 5,
            prefetch: '/portal/api/ilri/1/action/list_regions'
        }).on('typeahead:selected', function (e, d) {

            regionsTags.tagsManager("pushTag", d.value);

        });
    }

    //Countries
    if (document.getElementById("ILRI_prjcountries"))
    {
        countryTags = jQuery(".tm-ILRI_prjcountries").tagsManager({
                output: '#ILRI_prjcountries',
                onlyTagList: true,
                delimiters: [43],
                tagList: getTagList("/portal/api/ilri/1/action/list_countries"),
                tagsContainer: '#cnt-ILRI_prjcountries'
            }
        );

        jQuery(".tm-ILRI_prjcountries").typeahead({
            name: 'Countries',
            limit: 5,
            prefetch: '/portal/api/ilri/1/action/list_countries'
        }).on('typeahead:selected', function (e, d) {

            countryTags.tagsManager("pushTag", d.value);

        });
    }
    //Species
    if (document.getElementById("ILRI_prjspecies"))
    {
        speciesTags = jQuery(".tm-ILRI_prjspecies").tagsManager({
                output: '#ILRI_prjspecies',
                onlyTagList: true,
                tagList: getTagList("/portal/api/ilri/1/action/list_species"),
                tagsContainer: '#cnt-ILRI_prjspecies'
            }
        );

        jQuery(".tm-ILRI_prjspecies").typeahead({
            name: 'Species',
            limit: 5,
            prefetch: '/portal/api/ilri/1/action/list_species'
        }).on('typeahead:selected', function (e, d) {

            speciesTags.tagsManager("pushTag", d.value);

        });
    }

});





(function (jQuery) {

    //This fuction returs the list of tags from the JSON API in th form of an array. That is used as a taglist in tags managager


    //*************************** Project leve tags ************************************************************** 















    //Main document tags


    //****************************** Activity level tags ****************************************    

})(this.jQuery);

