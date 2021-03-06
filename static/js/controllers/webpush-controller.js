// Copyright (c) 2020 by Dan Jacob
// SPDX-License-Identifier: AGPL-3.0-or-later

import { postJSON } from '~/utils/fetch-json';
import { urlB64ToUint8Array } from '~/utils/encoders';
import ApplicationController from './application-controller';

let registration = null;

export default class extends ApplicationController {
  static targets = ['subscribe', 'unsubscribe'];
  static values = {
    csrfToken: String,
    publicKey: String,
    serviceWorkerUrl: String,
    subscribeUrl: String,
    subscribeMessage: String,
    unsubscribeUrl: String,
    unsubscribeMessage: String,
  };

  connect() {
    // check browser can do notifications, and permission OK.
    try {
      this.checkConfiguration();
      this.checkBrowserCompatibility();
      this.registerServiceWorker();
    } catch (e) {
      this.element.remove();
      console.warn('Webpush', e.toString());
    }
  }

  registerServiceWorker() {
    const onRegister = (swRegistration) => {
      registration = swRegistration;
      return registration.pushManager.getSubscription().then((subscription) => {
        if (subscription) {
          this.showUnsubscribe();
        } else {
          this.showSubscribe();
        }
      });
    };

    return navigator.serviceWorker
      .getRegistration(this.serviceWorkerValue)
      .then((swRegistration) => {
        if (swRegistration) {
          console.log('found existing service worker');
          return onRegister(swRegistration);
        }
        console.log('registering new service worker');
        return navigator.serviceWorker
          .register(this.serviceWorkerUrlValue)
          .then(onRegister);
      });
  }

  subscribe(event) {
    event.preventDefault();
    const options = {
      applicationServerKey: urlB64ToUint8Array(this.publicKeyValue),
      userVisibleOnly: true,
    };
    registration.pushManager.subscribe(options).then((subscription) => {
      this.showUnsubscribe();
      return this.syncWithServer(
        subscription,
        this.subscribeUrlValue,
        this.subscribeMessageValue
      );
    });
  }

  unsubscribe(event) {
    event.preventDefault();
    this.showSubscribe();
    registration.pushManager
      .getSubscription()
      .then((subscription) =>
        subscription
          .unsubscribe()
          .then(
            this.syncWithServer(
              subscription,
              this.unsubscribeUrlValue,
              this.unsubscribeMessageValue
            )
          )
      );
  }

  async syncWithServer(subscription, url, message) {
    await postJSON(url, this.csrfTokenValue, subscription);
    if (message) {
      this.toaster.info(message);
    }
  }

  showSubscribe() {
    this.element.classList.remove('hidden');
    this.subscribeTarget.classList.remove('hidden');
    this.unsubscribeTarget.classList.add('hidden');
  }

  showUnsubscribe() {
    this.element.classList.remove('hidden');
    this.unsubscribeTarget.classList.remove('hidden');
    this.subscribeTarget.classList.add('hidden');
  }

  checkConfiguration() {
    if (!this.hasPublicKeyValue) {
      throw new Error('pubKey not available');
    }
  }

  checkBrowserCompatibility() {
    if (!('serviceWorker' in navigator)) {
      throw new Error('serviceWorker not available');
    }
    if (!('PushManager' in window)) {
      throw new Error('PushManager not available');
    }
    if (!('Notification' in window)) {
      throw new Error('Notification not available');
    }
    if (Notification.permission === 'denied') {
      throw new Error('Permission denied');
    }
  }
}
