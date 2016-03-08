/* IMPORTING REQUIRED LIBRARIES */
var Utilities = {};

Utilities.require = function (file, callback) {
    callback = callback ||
    function () {};
    var filenode;
    var jsfile_extension = /(.js)$/i;
    var cssfile_extension = /(.css)$/i;

    if (jsfile_extension.test(file)) {
        filenode = document.createElement('script');
        filenode.src = file;
        // IE
        filenode.onreadystatechange = function () {
            if (filenode.readyState === 'loaded' || filenode.readyState === 'complete') {
                filenode.onreadystatechange = null;
                callback();
            }
        };
        // others
        filenode.onload = function () {
            callback();
        };
        document.head.appendChild(filenode);
    } else if (cssfile_extension.test(file)) {
        filenode = document.createElement('link');
        filenode.rel = 'stylesheet';
        filenode.type = 'text/css';
        filenode.href = file;
        document.head.appendChild(filenode);
        callback();
    } else {
        console.log("Unknown file type to load.")
    }
};

Utilities.requireFiles = function () {
    var index = 0;
    return function (files, callback) {
        index += 1;
        Utilities.require(files[index - 1], callBackCounter);

        function callBackCounter() {
            if (index === files.length) {
                index = 0;
                callback();
            } else {
                Utilities.requireFiles(files, callback);
            }
        }
    };
}();

function start(map_id, SERVER, REFRESH, ICON_SIZE) {
    Utilities.requireFiles(['http://code.jquery.com/jquery-2.0.3.js', 'http://cdn.leafletjs.com/leaflet-0.7.2/leaflet.css', 'http://cdn.leafletjs.com/leaflet-0.7.2/leaflet.js', 'lib/leaflet.label.js'], function() {
        var ICON_ANCHOR = [ICON_SIZE[0]/2, ICON_SIZE[1]/2];
        var LABEL_ANCHOR = [ICON_ANCHOR[0] + 2 - 6, 0];
        var INIT = [], STATIC_MARKERS = [], MARKERS = [], STATIC_POLYLINES = [], POLYLINES = [], STATIC_CIRCLES = [], CIRCLES = [];
        var MARKER_IN_INFO;

        /* INIT MAP */
        var mapboxUrl = 'https://{s}.tiles.mapbox.com/v3/{styleId}/{z}/{x}/{y}.png',
            osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
        var minimal         = L.tileLayer(mapboxUrl, {styleId: 'examples.map-i875kd35', maxZoom: 18}),
            osm         = L.tileLayer(osmUrl, {maxZoom: 18}),
            satellite   = L.tileLayer(mapboxUrl, {styleId: 'examples.map-qfyrx5r8', maxZoom: 18}),
            midnight    = L.tileLayer(mapboxUrl, {styleId: 'examples.map-0l53fhk2',   maxZoom: 18});
        var map = L.map(map_id, {
            center: new L.LatLng(46.856578, 2.351828),
            zoom: 6,
            layers: osm
        });

        /* SETTING LAYERS */
        var baseMaps = {
            "Satellite": satellite,
            "OpenStreetMap": osm,
            "Minimal": minimal,
            "Night View": midnight
        };
        L.control.layers(baseMaps).addTo(map);
        $('.leaflet-control-layers-base').append($("<hr/>"));

        var polylinesCheckbox = createControlCheckbox("Polylines", "nbPolylines", STATIC_POLYLINES, POLYLINES),
            markersCheckbox = createControlCheckbox("Icônes", "nbMarkers", STATIC_MARKERS, MARKERS),
            circlesCheckbox = createControlCheckbox("Cercles", "nbCircles", STATIC_CIRCLES, CIRCLES);

        /* INIT INFO BLOCK */
        var infoBlock = createInfoBlock('info'),
            errorBlock = createInfoBlock('error', 'bottomleft'),
            dateBlock = createInfoBlock('date', 'topleft');

        /* Displaying labels on big zoom */
        map.on('zoomend', showLabelsOnZoom);

        getInit();

        function getInit() {
            /* GET INIT SCRIPT */
            $.ajax({
                type: 'GET',
                dataType: "json",
                url: SERVER + "init",
                async: false,
                data: {},
                success: function(data) {
                    $('#error').hide();
                    INIT = data;
                    loadStatic(data, 'polylines', 'static_polyline');
                    loadStatic(data, 'objects', 'static_object');
                    loadStatic(data, 'circles', 'static_circle');
                },
                error: function() {
                    var html = '<b><span style="color:red">Erreur :</span></b><br/>';
                    html += "Impossible de se connecter à la source de données." + '<br/>';
                    html += "Reconnexion en cours...";
                    errorBlock.update(html);
                    getInit();
                }
            });
        }

        if(INIT['initZoom'] != undefined) {
            map.setZoom(INIT['initZoom']);
        }
        if(INIT['initLat'] != undefined && INIT['initLng'] != undefined) {
            map.panTo(new L.LatLng(INIT['initLat'], INIT['initLng']));
        }

        getData();
        setInterval(getData, REFRESH);

        function getData() {
            $.ajax({
                type: 'GET',
                dataType: "json",
                url: SERVER + "data",
                async: true,
                data: {},
                success: function(data) {
                    if(data == "null") return;

                    var new_objects = [], new_polylines = [], new_circles = [];
                    $.each( data, function(i, val) {
                        if(val.type != "date" && (val.name === undefined || val.id === undefined)) {
                            formatError("Data", "name et id", "");
                            return;
                        }
                        var object_key = val.name + val.id;

                        switch(val.type) {
                            case "object":
                                if(val.x === undefined || val.y === undefined) {
                                    formatError("Data", "x et y", val.name);
                                    return;
                                }

                                new_objects.push(object_key);
                                if(MARKERS[object_key] === undefined) {
                                    MARKERS[object_key] = createMarker(val, INIT["images"][val.name]["default"]);
                                    if(map.getZoom() > 14)
                                        MARKERS[object_key].showLabel();
                                } else {
                                    var latLng = MARKERS[object_key].getLatLng();
                                    // si le label existe déjà, on change sa position SEULEMENT si elle a changé
                                    // (grosse opti, surtout pour showLabel() qui est un gouffre de perfs)
                                    if(latLng.lat != val.x || latLng.lng != val.y) {
                                        MARKERS[object_key].setLatLng([val.x, val.y]);
                                        if(map.getZoom() > 14)
                                            MARKERS[object_key].showLabel();
                                    }

                                    if(MARKER_IN_INFO == object_key) {
                                        metadataToInfo(val, object_key);
                                    }
                                }

                                // On cherche si, dans les params de l'objet, on a un booléen à True
                                var timeToBreak = false;
                                Object.keys(val).some(function(key) {
                                    if(val[key] == "True" || val[key] == true) {
                                        // Si c'est le cas, on change l'image de l'objet avec l'image correspondant
                                        // à ce booléen dans INIT
                                        Object.keys(INIT["images"][val.name]).some(function(k) {
                                            if(key == k) {
                                                MARKERS[object_key].setIcon(L.icon({
                                                    iconUrl: INIT["images"][val.name][key],
                                                    iconSize:     ICON_SIZE,
                                                    iconAnchor:   ICON_ANCHOR,
                                                    labelAnchor: LABEL_ANCHOR
                                                }));
                                                timeToBreak = true;
                                                return true;
                                            } else return false;
                                        });
                                   }
                                   return timeToBreak;
                                });
                                // Si on n'a pas trouvé de booléen justifiant un changement d'icône, on utilise la default
                                if(!timeToBreak && "default" in INIT["images"][val.name]) {
                                    MARKERS[object_key].setIcon(L.icon({
                                        iconUrl: INIT["images"][val.name]["default"],
                                        iconSize:     ICON_SIZE,
                                        iconAnchor:   ICON_ANCHOR,
                                        labelAnchor: LABEL_ANCHOR
                                    }));
                                }

                                addObjectListeners(MARKERS[object_key], val, object_key, markersCheckbox);
                                break;

                            case "polyline":
                                if(val.points === undefined) {
                                    formatError("Data", "points", "polyline");
                                    return;
                                }

                                var points = [];
                                val.points.forEach(function(point) {
                                    if(point.x === undefined || point.y === undefined) {
                                       formatError("Data", "x et y", "points");
                                       return;
                                   }
                                   points.push([point.x, point.y])
                                });
                                if(points == []) return;

                                new_polylines.push(object_key);
                                if(POLYLINES[object_key] === undefined) {
                                    POLYLINES[object_key] = createPolyline(val, points);
                                } else {
                                    POLYLINES[object_key].setLatLngs(points);

                                    if(MARKER_IN_INFO == object_key) {
                                        metadataToInfo(val, object_key);
                                    }
                                }

                                addObjectListeners(POLYLINES[object_key], val, object_key, polylinesCheckbox);
                                break;

                            case "circle":
                                if(val.x === undefined || val.y === undefined) {
                                    formatError("Data", "x et y", val.name);
                                    return;
                                }
                                if(val.radius === undefined) {
                                    formatError("Data", "radius", val.name);
                                    return;
                                }

                                new_circles.push(object_key);
                                if(CIRCLES[object_key] === undefined) {
                                    CIRCLES[object_key] = createCircle(val);
                                } else {
                                    CIRCLES[object_key].setLatLng([val.x, val.y]);
                                    CIRCLES[object_key].setRadius(val.radius);

                                    if(MARKER_IN_INFO == object_key) {
                                        metadataToInfo(val, object_key);
                                    }
                                }

                                addObjectListeners(CIRCLES[object_key], val, object_key, circlesCheckbox);
                                break;

                            case "date":
                                var html = '<b>Date : </b> ' + val.date + '<br/>';
                                html += '<b>Heure : </b> ' + val.time + '<br/>';
                                dateBlock.update(html);
                                break;
                        }
                    });

                    // On cherche les objets et polylines qui ont disparu depuis la dernière màj
                    // et on supprime leur marqueur + le bloc info s'il affichait le marqueur disparu
                    // N.B.: On le fait ici pour des questions de perfs, recréer les listes MARKERS et POLYLINES
                    // à chaque success() est TRES coûteux.
                    removeDeletedObjects(MARKERS, new_objects);
                    removeDeletedObjects(POLYLINES, new_polylines);
                    removeDeletedObjects(CIRCLES, new_circles);

                    $('#nbMarkers').text(" (" + (Object.keys(STATIC_MARKERS).length + Object.keys(MARKERS).length) + ")");
                    $('#nbPolylines').text(" (" + (Object.keys(STATIC_POLYLINES).length + Object.keys(POLYLINES).length) + ")");
                    $('#nbCircles').text(" (" + (Object.keys(STATIC_CIRCLES).length + Object.keys(CIRCLES).length) + ")");
                },
                error: function() {
                    var html = '<b><span style="color:red">Erreur :</span></b><br/>';
                    html += "Une connexion à la source de données a échoué." + '<br/>';
                    errorBlock.update(html);
                }
            });
        }

        function createMarker(val, image) {
            var marker = L.marker([val.x, val.y]).setIcon(L.icon({
                iconUrl: image,
                iconSize:     ICON_SIZE,
                iconAnchor:   ICON_ANCHOR,
                labelAnchor: LABEL_ANCHOR
            }));
            if(val.label != undefined) {
                // setIcon() doit toujours être appelée AVANT bindLabel() sinon il ne se place pas bien
                marker.bindLabel(val.label, {noHide: false});
            }
            return marker.addTo(map);
        }

        function createPolyline(val, points) {
            var opacity = val.opacity != undefined ? val.opacity : 0.5,
                color = val.color != undefined ? val.color : 'blue';
            return L.polyline(points, {color: color, opacity: opacity }).addTo(map);
        }

        function createCircle(val) {
            var color = val.color != undefined ? val.color : 'blue',
                fillColor = val.fillColor != undefined ? val.fillColor : 'blue',
                fillOpacity = val.fillOpacity != undefined ? val.fillOpacity : 0.5;
            return L.circle([val.x, val.y], val.radius, {
                color: color,
                fillColor: fillColor,
                fillOpacity: fillOpacity
            }).addTo(map);
        }

        function metadataToInfo(val, object_key) {
            if(val.metadata === undefined) {
                MARKER_IN_INFO = null;
                $('#info').hide();
                return;
            }
            object_key = object_key || undefined;

            var html = "<b>Info :</b><br/>";
            $.each( val.metadata, function(i, md) {
                html += md + "<br/>";
            });
            infoBlock.update(html);
            MARKER_IN_INFO = object_key;
        }

        function formatError(location, missingParam, parent) {
            var html = '<b><span style="color:red">Erreur :</span></b><br/>';
            html += "Données ignorées car mal formatées dans le script " + location + '.<br/>';
            html += "L'objet " + parent + " doit contenir un attribut " + missingParam + ".";
            errorBlock.update(html);
        }

        function createInfoBlock(id, position) {
            position = position || 'topright';
            var block = L.control({'position': position});
            block.onAdd = function (map) {
                var jdiv = $("<div/>").addClass('info').attr('id', id).click(function() {
                    $(this).hide();
                    if(MARKER_IN_INFO) MARKER_IN_INFO = null;
                });
                this._div = jdiv.get(0);
                this.update("");
                return this._div;
            };
            block.update = function(html) {
                $("#" + id).show();
                this._div.innerHTML = html;
            };
            block.addTo(map);
            $("#" + id).hide();
            return block;
        }

        function createControlCheckbox(checkbox_name, checkbox_id, static_objects, objects) {
            var checkbox = $("<input/>")
            .attr("type", "checkbox")
            .attr("checked", "checked")
            .click(function() {
                if($(this).is(':checked')) {
                    showAll(static_objects);
                    showAll(objects);
                } else {
                    hideAll(static_objects);
                    hideAll(objects);
                }
            });
            $('.leaflet-control-layers-base').append($("<label/>").append(checkbox).append($("<span/>").text(checkbox_name)).append($("<span/>").attr("id", checkbox_id)));
            return checkbox;
        }

        function loadStatic(data, object_name, key_name) {
            if(data[object_name] != undefined) {
                data[object_name].forEach(function(object) {
                    object.id = data[object_name].indexOf(object);
                    var object_key = key_name + object.id;
                    var current, checkbox;

                    switch(object_name) {
                        case 'polylines':
                            if(object.points === undefined) {
                                formatError("Init", "points", "polyline");
                                return;
                            }

                            var points = [];
                            object.points.forEach(function(point) {
                               if(point.x === undefined || point.y === undefined) {
                                   formatError("Init", "x et y", "points");
                                   return;
                               }
                               points.push([point.x, point.y])
                            });
                            if(points == []) return;

                            current = STATIC_POLYLINES[object_key] = createPolyline(object, points);
                            checkbox = polylinesCheckbox;
                            break;

                        case 'objects':
                            if(object.x === undefined || object.y === undefined) {
                                formatError("Init", "x et y", "objects");
                               return;
                            }
                            if(object.image === undefined) {
                                formatError("Init", "image", "objects");
                               return;
                            }
                            current = STATIC_MARKERS[object_key] = createMarker(object, object.image);
                            checkbox = markersCheckbox;
                            break;

                        case 'circles':
                            if(object.x === undefined || object.y === undefined) {
                                formatError("Init", "x et y", "circles");
                               return;
                            }
                            if(object.radius === undefined) {
                                formatError("Init", "radius", "circles");
                               return;
                            }
                            current = STATIC_CIRCLES[object_key] = createCircle(object);
                            checkbox = circlesCheckbox;
                            break;
                    }

                    addObjectListeners(current, object, object_key, checkbox);
                });
            }
        }

        function addObjectListeners(map_object, object, object_key, checkbox) {
            map_object.removeEventListener();
            map_object.on('click', function() {
                if($.isFunction(this.getLatLng)) {
                    map.panTo(this.getLatLng(), {animate: true});
                }
                metadataToInfo(object, object_key);
            }).on('contextmenu', function() {
                if(MARKER_IN_INFO == object_key) {
                    MARKER_IN_INFO = null;
                    $('#info').hide();
                }
                checkbox.get(0).indeterminate = true;
                hide(this);
            });
        }

        function removeDeletedObjects(old_objects, new_objects) {
            Object.keys(old_objects).forEach(function(old_object) {
                var trouve = false;
                new_objects.some(function(new_object) {
                    if(old_object == new_object) {
                        trouve = true;
                        return true;
                    } else return false;
                });
                if(!trouve) {
                    old_objects[old_object].hideLabel();
                    map.removeLayer(old_objects[old_object]);
                    delete old_objects[old_object];
                    if(MARKER_IN_INFO == old_object) {
                        $('#info').hide();
                    }
                }
            });
        }

        function showLabelsOnZoom() {
            if(map.getZoom() > 14) {
                Object.keys(MARKERS).forEach(function(marker) {
                    MARKERS[marker].showLabel();
                });
                Object.keys(STATIC_MARKERS).forEach(function(marker) {
                    STATIC_MARKERS[marker].showLabel();
                });
            } else {
                Object.keys(MARKERS).forEach(function(marker) {
                    MARKERS[marker].hideLabel();
                });
                Object.keys(STATIC_MARKERS).forEach(function(marker) {
                    STATIC_MARKERS[marker].hideLabel();
                });
            }
        }

        function show(object) {
            if(!map.hasLayer(object)) {
                map.addLayer(object);
                if(map.getZoom() > 14)
                    object.showLabel && object.showLabel();
            }
        }

        function showAll(objects) {
            Object.keys(objects).forEach(function(object) {
                show(objects[object]);
            });
        }

        function hide(object) {
            if(map.hasLayer(object)) {
                map.removeLayer(object);
                object.hideLabel && object.hideLabel();
            }
        }

        function hideAll(objects) {
            Object.keys(objects).forEach(function(object) {
                hide(objects[object]);
            });
        }
    });
}