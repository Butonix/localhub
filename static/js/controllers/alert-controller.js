// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { fadeOut } from '~/utils/dom-helpers';
import ApplicationController from './application-controller';

export default class extends ApplicationController {
  /*
  Used with an server-side rendered alert element that "fades out" after a few seconds
  after page load.

  */
  connect() {
    this.timeout = setTimeout(() => {
      this.dismiss();
      clearTimeout(this.timeout);
    }, 3000);
  }

  dismiss() {
    fadeOut(this.element, () => this.element.remove());
  }
}
