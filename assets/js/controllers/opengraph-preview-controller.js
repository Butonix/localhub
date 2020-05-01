// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import axios from 'axios';

import {
  EVENT_FORM_COMPLETE,
  EVENT_FORM_FETCHING,
  TOAST_ERROR,
} from '@utils/application-constants';

import ApplicationController from './application-controller';

export default class extends ApplicationController {
  static targets = [
    'description',
    'descriptionPreview',
    'fullPreview',
    'image',
    'imagePreview',
    'input',
    'listener',
    'title',
  ];

  fetch(event) {
    event.preventDefault();

    if (!this.inputTarget.checkValidity()) {
      return false;
    }

    const url = this.inputTarget.value;

    if (!url) {
      this.deleteFetchedUrl();
      this.clearPreview();
      return false;
    }

    if (this.isFetchedUrl(url)) {
      return false;
    }

    this.clearPreview();

    // prevent refetch
    const { currentTarget } = event;

    currentTarget.setAttribute('disabled', true);
    this.disableFormControls();

    axios
      .get(this.data.get('preview-url'), { params: { url } })
      .then((response) => {
        const { title, description, image, url } = response.data;

        if (url) {
          this.inputTarget.value = url;
        }

        this.updatePreview(title, description, image);
        this.updateListeners({ title, image, description });

        this.updateFetchedUrl(url);
      })
      .catch(() => this.handleServerError())
      .finally(() => {
        this.enableFormControls();
        currentTarget.removeAttribute('disabled');
      });
  }

  disableFormControls() {
    this.publish(EVENT_FORM_FETCHING);
  }

  enableFormControls() {
    this.publish(EVENT_FORM_COMPLETE);
  }

  clearListeners() {
    Array.from(this.listenerTargets).forEach((target) => (target.value = ''));
  }

  updateListeners(data) {
    Object.keys(data).forEach((name) => {
      Array.from(this.listenerTargets)
        .filter(
          (target) =>
            target.getAttribute(`data-${this.identifier}-listener-value`) === name
        )
        .forEach((target) => {
          target.value = data[name];
        });
    });
  }

  clearPreview() {
    this.titleTarget.innerText = '';
    this.titleTarget.classList.add('d-none');

    this.descriptionTargets.forEach((el) => {
      el.innerText = '';
    });

    this.imageTargets.forEach((el) => {
      el.setAttribute('src', '');
    });

    [
      this.fullPreviewTarget,
      this.descriptionPreviewTarget,
      this.imagePreviewTarget,
      this.titleTarget,
    ].forEach((el) => el.classList.add('d-none'));
  }

  updatePreview(title, description, image) {
    if (title) {
      this.titleTarget.innerText = title;
      this.titleTarget.classList.remove('d-none');
    }

    if (description) {
      Array.from(this.descriptionTargets).forEach((el) => (el.innerText = description));
    }

    if (image) {
      Array.from(this.imageTargets).forEach((el) => el.setAttribute('src', image));
    }

    if (description && image) {
      this.fullPreviewTarget.classList.remove('d-none');
    } else if (description) {
      this.descriptionPreviewTarget.classList.remove('d-none');
    } else if (image) {
      this.imagePreviewTarget.classList.remove('d-none');
    }
  }

  deleteFetchedUrl() {
    this.data.delete('fetchedUrl');
  }

  updateFetchedUrl(url) {
    this.data.set('fetchedUrl', url.trim());
  }

  isFetchedUrl(url) {
    if (!this.data.has('fetchedUrl')) {
      return false;
    }
    return this.data.get('fetchedUrl').trim() === url.trim();
  }

  handleServerError() {
    this.clearListeners();
    this.toast(TOAST_ERROR, this.data.get('errorMessage'));
  }
}
