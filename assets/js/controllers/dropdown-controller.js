// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Controller } from 'stimulus';

export default class extends Controller {
  /*
    Manages dropdown and keeps the menu visible within the viewport.

    actions:
        toggle: toggles the dropdown menu

    targets:
        menu: the dropdown menu
  */
  static targets = ['menu'];

  connect() {
    document.addEventListener('click', () => {
      this.close();
    });
  }

  toggle(event) {
    event.preventDefault();
    event.stopPropagation();
    this.element.classList.toggle('active');
    const rect = this.menuTarget.getBoundingClientRect();
    // ensure menu always appears within viewport
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    let top, bottom, left, right;

    if (rect.bottom + rect.height > viewportHeight) {
      top = 'auto';
      bottom = 0;
    } else {
      top = 0;
      bottom = 'auto';
    }
    const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
    if (rect.left + rect.width > viewportWidth) {
      left = 'auto';
      right = 0;
    } else {
      right = 'auto';
      left = 0;
    }
    this.menuTarget.style.top = top;
    this.menuTarget.style.bottom = bottom;
    this.menuTarget.style.left = left;
    this.menuTarget.style.right = right;
  }

  close() {
    this.element.classList.remove('active');
  }
}