// Copyright (c) 2019 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import {
  Controller
} from 'stimulus';

const MAX_HEIGHT = 500;

export default class extends Controller {
  static targets = ['container', 'toggle'];

  initialize() {
    document.addEventListener(
      'turbolinks:render', () => this.checkContainerHeights()
    )
  }

  connect() {
    this.checkContainerHeights()
  }

  toggle(event) {
    event.preventDefault();
    this.containerTarget.classList.remove('collapsable');
    this.toggleTargets.forEach(el => el.classList.add('d-hide'));
  }

  checkContainerHeights() {
    this.checkContainerHeight();
    // ensure we check heights of all images and other dynamic elements
    // and handle when these are individually loaded
    for (const tag of ["img", "iframe"]) {
      for (const el of this.containerTarget.getElementsByTagName(tag)) {
        el.onload = () => this.checkContainerHeight();
      }
    }
  }

  checkContainerHeight() {
    // show "show more" button if container higher than max height
    if (this.containerTarget.offsetHeight < this.containerTarget.scrollHeight ||
      this.containerTarget.offsetHeight >= MAX_HEIGHT) {
      this.toggleTargets.forEach(el => el.classList.remove('d-hide'));
    }
  }
}
