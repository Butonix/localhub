// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import ApplicationController from './application-controller';

const DEFAULT_ZOOM = 13;

export default class extends ApplicationController {
  /*
  Inserts an OpenStreetMap into the element on page load.

  data:
    latitude
    longitude
    zoom: zoom level (default: 13)

  */
  connect() {
    // Leaflet library loaded in CDN
    const L = window.L;

    const coords = [this.latitude, this.longitude];
    const map = L.map(this.element.id).setView(coords, this.defaultZoom);

    L.tileLayer(this.tileLayer, {
      attribution:
        'Map data &copy; <a href="https://www.openstreetmap.org/">' +
        'OpenStreetMap</a> contributors,' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    }).addTo(map);

    const marker = L.marker(coords);
    const group = new L.featureGroup([marker]);
    L.marker(coords).addTo(map);
    map.fitBounds(group.getBounds());
    map.setZoom(this.defaultZoom);
    map.scrollWheelZoom.disable();
  }

  get tileLayer() {
    return 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  }

  get defaultZoom() {
    return parseInt(this.data.get('zoom') || DEFAULT_ZOOM, 10);
  }

  get latitude() {
    return parseFloat(this.data.get('latitude'));
  }

  get longitude() {
    return parseFloat(this.data.get('longitude'));
  }
}