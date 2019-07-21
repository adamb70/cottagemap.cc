	// Add zoom control
	map.addControl(new mapboxgl.NavigationControl());

	// Add geolocate control to the map.
	map.addControl(new mapboxgl.GeolocateControl({
		positionOptions: {
			enableHighAccuracy: true
		},
		trackUserLocation: true
	}));

	// Add text search
	map.addControl(new MapboxGeocoder({
		accessToken: mapboxgl.accessToken,
		countries: 'gb',
		mapboxgl: mapboxgl,
        collapsed: true,
        placeholder: 'Search locations'
	}), 'top-left');


    // Add custom marker toggles
	class MarkerToggleControl{
		constructor(options) {
            this.options = options;
        }

		onAdd(map) {
			this._map = map;

			// create button
            this._container = document.createElement('div');
            let button_container = document.createElement('div');
			button_container.classList.add('mapboxgl-ctrl', 'mapboxgl-ctrl-group');
			button_container.innerHTML = '<button id="layers-button" class="mapboxgl-ctrl-icon" type="button"></button>';
			button_container.addEventListener('click', this.on_button_click.bind(this));
			this._container.appendChild(button_container);

			// create select list
			this._selectlist = document.createElement('div');
			this._selectlist.id = 'layer-select';
			this._selectlist.className = 'mapboxgl-ctrl';

			for (let region_group in this.options.region_groups) {
				const label = document.createElement('div');
				label.setAttribute('data-region', region_group);
				let count = 0;

				for (let region of this.options.region_groups[region_group]) {
					count += REGIONS[region].length;
                }

                label.innerHTML = region_group + ' (' + count + ')';
				if (this.options.visible_regions.includes(region_group)) {
					label.classList.add('checked');
                }

                this._selectlist.appendChild(label);
                label.addEventListener('click', this.on_label_click.bind(this, label));
            }
			this._container.appendChild(this._selectlist);

			return this._container;
		}

		init_markers() {
			// build empty lists for regions that aren't visible yet
			for (const region in REGIONS) {
                REGION_MARKERS[region] = [];
            }

			for (let selected of this.options.visible_regions) {
				for (let region of this.options.region_groups[selected]) {
					generate_markers(region);
				}
			}
        }

		onRemove() {
			this._selectlist.parentNode.removeChild(this._selectlist);
			this._map = undefined;
		}

		on_label_click(label) {
			if (!label.classList.contains('checked')) {
				// show regions
                label.classList.add('checked');
				for (let region of this.options.region_groups[label.getAttribute('data-region')]) {
					delete_region_markers(region);
					generate_markers(region);
                }
            } else {
			    // delete regions
                label.classList.remove('checked');
                for (let region of this.options.region_groups[label.getAttribute('data-region')]) {
                	delete_region_markers(region);
                }
            }
        }

        outside_click(event) {
            if (!this._container.contains(event.target)) {
                this._selectlist.classList.remove('open');
                document.removeEventListener('click', this._bound_listener)
            }
        }

        on_button_click() {
			if (this._selectlist.classList.contains('open')) {
				this._selectlist.classList.remove('open');
       			document.removeEventListener('click', this._bound_listener)
            } else {
				this._selectlist.classList.add('open');
				this._bound_listener = this.outside_click.bind(this);
       			document.addEventListener('click', this._bound_listener)
            }
        }
	}
	const marker_control = new MarkerToggleControl({
        region_groups: REGION_GROUPS,
        visible_regions: ['north west england']
    });
	map.addControl(marker_control, 'top-right');

	const format_boolean = function (bool) {
		return bool ? '<i class="fas fa-check"></i>' : '<i class="fas fa-times"></i>'
	};

	const resize = function (container) {
		// make sure dimensions are always even number and not a float, to avoid blurry text
		let newWidth = container.offsetWidth;
		if (container.offsetWidth % 2 !== 0)
			newWidth++;
		container.style.width = newWidth + 'px';
		container.style.maxWidth = newWidth + 'px';

		let newHeight = container.offsetHeight;
		if (container.offsetHeight % 2 !== 0)
			newHeight++;
		container.style.height = newHeight + 'px';
		container.style.maxHeight = newHeight + 'px';
	};

	const generate_markers = function (region) {
		const generated_makers = [];
		const processed_lnglats = {};
		for (let cottage of REGIONS[region]) {

			// create a HTML element for each feature
			let el = document.createElement('div');
			el.classList.add('marker', region);

			let lnglat = new mapboxgl.LngLat(cottage.lon, cottage.lat);
			let offset_mult = 0;
			if (lnglat in processed_lnglats) {
				offset_mult = ++processed_lnglats[lnglat];
				// offset lnglat a little bit if markers are on the same coordinates
				lnglat = new mapboxgl.LngLat(parseFloat(cottage.lon) + (0.0001 * offset_mult), parseFloat(cottage.lat) - (0.0001 * offset_mult));
			} else {
				processed_lnglats[lnglat] = 0
			}


			let new_marker = new mapboxgl.Marker(el)
				.setLngLat(lnglat)
				.setPopup(new mapboxgl.Popup({offset: 25})
					.on('open', function (pop) {
						const _container = pop.target._container;

						// set image url
						let img = _container.getElementsByClassName('popup-img')[0];
						// wait until image dimensions are available
						img.src = cottage.image;
						let wait = setInterval(function () {
							let w = img.naturalWidth,
								h = img.naturalHeight;
							if (w && h) {
								clearInterval(wait);
								// resize container
								resize(_container);
							}
						}, 30);

						// attach late deals
						for (let offer of cottage.late_offers) {
							let deal_box = document.createElement('a');
							deal_box.classList.add('deal-box', 'mapboxgl-popup-content');
							deal_box.href = cottage.url + '#last-minute-offers';
							deal_box.target = cottage.ref;
							deal_box.innerHTML = '<span>Offer: </span>' + offer.offer;
							_container.appendChild(deal_box);
						}

						// center on marker
						let marker_rect = el.getBoundingClientRect();
						let marker_center = marker_rect.top + (marker_rect.height / 2);
						let offset_sign = -1;
						if (marker_center > window.innerHeight / 2) {
							offset_sign = 1;
						}
						map.flyTo({center: this.getLngLat(), offset: [0, window.innerHeight * 0.4 * offset_sign]});

					})
					.setHTML('<h3 class="cottage-title"><a href="' + cottage.url + '" target="' + cottage.ref + '">' + cottage.title + '</a></h3>'
						+ '<a href="https://www.google.com/maps/search/?api=1&query=' + cottage.lat + ',' + cottage.lon
						+ '" class="location" title="View on Google Maps" target="' + cottage.ref + '_map"><i class="fas fa-map-marker-alt"></i>'
						+ cottage.location + '</a><p class="description">' + cottage.description
						+ '</p><div class="weekly-price">Weekly price £' + cottage.weekly_low + ' to £' + cottage.weekly_high
						+ '</div><a href="' + cottage.url + '" target="' + cottage.ref + '"><img class="popup-img" src=""/></a><div class="details">'
						+ '<i class="fas fa-bed" title="Sleeps"></i> ' + cottage.sleeps + '<span class="detail-divider">|</span><i class="fas fa-door-open" title="Bedrooms"></i> ' +
						cottage.bedrooms + '<span class="detail-divider">|</span><i class="fas fa-dog" title="Dogs allowed"></i>' + format_boolean(cottage.dog) +
						'<span class="detail-divider">|</span><i class="fas fa-child" title="Child friendly"></i>' + format_boolean(cottage.child) +
						'<span class="detail-divider">|</span><i class="fas fa-wifi" title="Wifi"></i>' + format_boolean(cottage.wifi)))
				.addTo(map);

			generated_makers.push(new_marker);
		}
		REGION_MARKERS[region] = generated_makers
	};

	const genereate_all_markers = function () {
		for (const region in REGIONS) {
			generate_markers(region);
		}
	};

	const delete_region_markers = function (region) {
		for (const marker of REGION_MARKERS[region]) {
			marker.remove();
		}
		REGION_MARKERS[region] = [];
	};

	const delete_all_markers = function () {
		for (const region in REGIONS) {
			delete_region_markers(region);
		}
	};


	// init markers
	const REGION_MARKERS = {};
	marker_control.init_markers();
