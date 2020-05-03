// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Events, Keys } from '@utils/constants';
import { maximizeZIndex } from '@utils/dom-helpers';

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Handles confirmation modal dialog.

  targets:
    header: header of dialog
    body: main content of dialog

  actions:
    cancel: if "cancel" button is clicked
    confirm: if "confirm" button is clicked
    keydown: windows key events
  */
  static targets = ['header', 'body'];

  connect() {
    this.bus.sub(Events.CONFIRM_OPEN, (event) => this.open(event));
  }

  keydown(event) {
    if (event.keyCode === Keys.ESC) {
      this.close();
    }
  }

  open({ detail: { header, body, onConfirm } }) {
    this.headerTarget.innerText = header;
    this.bodyTarget.innerText = body;
    this.onConfirm = onConfirm;
    this.element.classList.add('active');
    maximizeZIndex(this.element);
  }

  close() {
    this.onConfirm = null;
    this.element.classList.remove('active');
  }

  cancel(event) {
    event.preventDefault();
    this.close();
  }

  confirm(event) {
    event.preventDefault();
    if (this.onConfirm) {
      this.onConfirm();
      this.onConfirm = null;
    }
    this.close();
  }
}
