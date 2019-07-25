	const hashCode = s => {
		let h, i;
		for (i = h = 0; i < s.length; i++) {
			h = Math.imul(31, h) + s.charCodeAt(i) | 0;
		}
		return h;
	};

	function timeSince(date) {
		const seconds = Math.floor((new Date() - date) / 1000);
		let interval = Math.floor(seconds / 31536000);
		if (interval > 1) {
			return interval + " years";
		}
		interval = Math.floor(seconds / 2592000);
		if (interval > 1) {
			return interval + " months";
		}
		interval = Math.floor(seconds / 86400);
		if (interval > 1) {
			return interval + " days";
		}
		interval = Math.floor(seconds / 3600);
		if (interval > 1) {
			return interval + " hours";
		}
		interval = Math.floor(seconds / 60);
		if (interval > 1) {
			return interval + " minutes";
		}
		return Math.floor(seconds) + " seconds";
	}

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
			this._selectlist.addEventListener('animationend', this.selectlist_animation_end.bind(this));

			for (let region_group in this.options.region_groups) {
				const label = document.createElement('div');
				label.setAttribute('data-region', region_group);
				let count = 0;

				let update_time;
				for (let region of this.options.region_groups[region_group]) {
					count += REGIONS[region].length;
					// Just take the update time from the last region, they will all be updated at the same time
					update_time = UPDATE_TIMES[region]
                }

                label.innerHTML = region_group + ' (' + count + ')<small>Updated ' + timeSince(update_time) + ' ago</small>';
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
                if (stored_viewed[region] === undefined) {
					stored_viewed[region] = {}
				}
            }
			localStorage.setItem('viewedCottages', JSON.stringify(stored_viewed));

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

        selectlist_animation_end() {
			if (this._container.classList.contains('open')) {
				// opening
				this._selectlist.classList.remove('fadeInLayerSelect')
			} else {
				// closing
				this._selectlist.classList.remove('fadeOutLayerSelect')
			}
		}

        outside_click(event) {
            if (!this._container.contains(event.target)) {
                this._container.classList.remove('open');
				this._selectlist.classList.add('fadeOutLayerSelect');
                document.removeEventListener('click', this._bound_listener)
            }
        }

        on_button_click() {
			if (this._container.classList.contains('open')) {
				// close
				this._container.classList.remove('open');
				this._selectlist.classList.add('fadeOutLayerSelect');
				document.removeEventListener('click', this._bound_listener)
            } else {
				// open
				this._container.classList.add('open');
				this._selectlist.classList.add('fadeInLayerSelect');
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
			el.classList.add('marker', region, 'ref-'+cottage.ref);

			const viewed_data = stored_viewed[region][cottage.ref];
			if (viewed_data) {
				el.classList.add('viewed');

				for (let offer of cottage.late_offers) {
					let hash = hashCode(offer.offer);
					if (!viewed_data[0].includes(hash)) {
						// job has a new offer
						el.classList.remove('viewed');
						el.classList.add('new');
						el.innerHTML = '<span class="new-deal" title="New offer since you last clicked this property"><i class="fas fa-star-of-life"></i></span>';
						break;
					}
				}

			}

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

						stored_viewed = localStorage.getItem('viewedCottages');
						stored_viewed  = stored_viewed ? JSON.parse(stored_viewed) : {};

						if (typeof stored_viewed[region] === 'undefined') {
							stored_viewed[region] = {};
						}

						const viewed_cottage = stored_viewed[region][cottage.ref];
						let stored_deals, time;
						if (typeof viewed_cottage !== 'undefined') {
							stored_deals = viewed_cottage[0];
							//time = new Date(viewed_cottage[1]);
						}

						//if (time && new Date().getTime() > time.getTime()) {
							// do stuff with the time?
						//}

						let flag = false;
						const new_deals = [];
						// attach late deals
						for (let offer of cottage.late_offers) {
							let deal_box = document.createElement('a');
							deal_box.classList.add('deal-box', 'mapboxgl-popup-content');
							deal_box.href = cottage.url + '#last-minute-offers';
							deal_box.target = cottage.ref;

							const offer_hash = hashCode(offer.offer);
							if (stored_deals && !stored_deals.includes(offer_hash))
							{
								deal_box.innerHTML = '<span class="new-deal" title="New since you last viewed"><i class="fas fa-star-of-life"></i></span>';
								flag = true;
							}

							deal_box.innerHTML += '<span>Offer: </span>' + offer.offer;
							_container.appendChild(deal_box);
							new_deals.push(offer_hash);
						}

						// store cottage offers as visited
						stored_viewed[region][cottage.ref] = [new_deals, new Date()];
						localStorage.setItem('viewedCottages', JSON.stringify(stored_viewed));
						el.classList.add('viewed');
						el.classList.remove('new');
						el.innerHTML = '';

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
	let stored_viewed = localStorage.getItem('viewedCottages');
	stored_viewed  = stored_viewed ? JSON.parse(stored_viewed) : {};
	const REGION_MARKERS = {};
	marker_control.init_markers();
