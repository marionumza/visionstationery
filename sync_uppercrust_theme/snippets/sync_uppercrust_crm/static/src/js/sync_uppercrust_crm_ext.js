$(document).ready(function() {
    var txt_ids = $('.st-cntct-form .box-item .st-text');
    _.each(txt_ids, function(txt_id){
        $(txt_id).on('focus click',function(){
            $(this).parent().find('label').css('opacity', 0);
            $(this).css('border', '1px solid #c3c3c3')
        })
        .blur(function(){
            if ($(txt_id).val() == '') {
             $(this).parent().find('label').css('opacity', 1);
                 $(this).css('border', '1px solid #f4f4f4')
            }
        });
    });
    // Read Map
    $('#map_canvas').initUCGoogleMap();
});

(function() {
    "use strict";
    $.fn.initUCGoogleMap = function(options) {
        var mapCanvas = $('#map_canvas');

        var defaults = {
            latitude: 0.0,
            longitude: 0.0,
            zoom: 16,
            type: 'ROADMAP',
            marker: {
                latitude: 0.0,
                longitude: 0.0,
                title: mapCanvas.data('res_company_name'),
                open: false,
                center: true
            },
            styles: 'GRAYSCALE',
        };

        var options = $.extend(defaults, options);
        var geoLocalize = mapCanvas.data('geo_localize');
        var infoWindow = new google.maps.InfoWindow();
        var Geocoder = new google.maps.Geocoder();

        var map = new google.maps.Map(document.getElementById($(this).attr('id')), {
            center: options.marker.center ? new google.maps.LatLng(options.marker.latitude, options.marker.longitude) : new google.maps.LatLng(options.latitude, options.longitude),
            zoom: options.zoom,
            mapTypeId: eval('google.maps.MapTypeId.' + options.type)
        });

        google.maps.event.addListener(map, 'click', function() {
            infoWindow.close();
        });

        var onMarkerClick = function() {
            var marker = this;
            infoWindow.setContent('<div class="marker" style="text-align:center;"><b>'+marker.title+'</b><br/>'+marker.address+'<br/>'+marker.position+'</div>');
            infoWindow.open(map, marker);
        };

        if (geoLocalize){
            if (!options.latitude && !options.longitude) {
                Geocoder.geocode({'address': geoLocalize}, function(results, status) {
                    if (status === google.maps.GeocoderStatus.OK) {
                        var location = results[0].geometry.location;
                        map.setCenter(location);
                        var marker = new google.maps.Marker({
                            title: options.marker.title,
                            address: geoLocalize,
                            map: map,
                            position: location
                        });
                        google.maps.event.addListener(marker, 'click', onMarkerClick);
                    } else {
                        console.debug('Geocode was not successful for the following reason: ' + status);
                    }
                });
            } else {
                var latLng = new google.maps.LatLng(options.latitude, options.longitude);
                map.setCenter(latLng);
                var marker = new google.maps.Marker({
                    title: options.marker.title,
                    address: geoLocalize,
                    map: map,
                    position: latLng
                });
                google.maps.event.addListener(marker, 'click', onMarkerClick);
            }
        }
    };
})(jQuery);