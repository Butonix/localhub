# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.encoding import smart_text
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from icalendar import Calendar
from icalendar import Event as CalendarEvent
from timezone_field import TimeZoneField

from localhub.apps.activities.models import Activity
from localhub.common.db.search.indexer import SearchIndexer
from localhub.common.utils.http import get_domain
from localhub.notifications.decorators import dispatch

from .managers import EventManager


class Event(Activity):

    # not exhaustive!

    ADDRESS_FORMATS = [
        (
            ("GB", "IN", "PK", "ZA", "JP"),
            "{street_address}, {locality}, {region}, {postcode}, {country}",
        ),
        (
            ("US", "AU", "NZ"),
            "{street_address} {locality}, {postcode}, {region}, {country}",
        ),
        (("RU",), "{street_address} {locality} {postcode}, {region}, {country}",),
    ]

    # default for Europe, S. America, China, S. Korea
    DEFAULT_ADDRESS_FORMAT = (
        "{street_address}, {postcode} {locality}, {region}, {country}"
    )

    LOCATION_FIELDS = [
        "street_address",
        "locality",
        "postal_code",
        "region",
        "country",
    ]

    RESHARED_FIELDS = (
        Activity.RESHARED_FIELDS
        + LOCATION_FIELDS
        + [
            "url",
            "starts",
            "ends",
            "timezone",
            "venue",
            "ticket_price",
            "ticket_vendor",
            "latitude",
            "longitude",
        ]
    )

    class InvalidDate(ValueError):
        """Used with date queries"""

        ...

    class RepeatChoices(models.TextChoices):
        DAILY = "day", _("Same time every day")
        WEEKLY = "week", _("Same day of the week at the same time")
        MONTHLY = (
            "month",
            _("First day of the month at the same time"),
        )
        YEARLY = "year", _("Same date and time every year")

    url = models.URLField(verbose_name=_("Link"), max_length=500, null=True, blank=True)

    starts = models.DateTimeField(verbose_name=_("Starts on (UTC)"))
    # Note: "ends" must be same day if repeating
    ends = models.DateTimeField(null=True, blank=True)

    repeats = models.CharField(
        max_length=20, choices=RepeatChoices.choices, null=True, blank=True
    )
    repeats_until = models.DateTimeField(null=True, blank=True)

    timezone = TimeZoneField(default=settings.TIME_ZONE)

    canceled = models.DateTimeField(null=True, blank=True)

    venue = models.CharField(max_length=200, blank=True)

    ticket_price = models.CharField(max_length=200, blank=True)
    ticket_vendor = models.TextField(
        verbose_name=_("Tickets available from"), blank=True
    )

    contact_name = models.CharField(max_length=200, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_email = models.EmailField(blank=True)

    street_address = models.CharField(max_length=200, blank=True)
    locality = models.CharField(
        verbose_name=_("City or town"), max_length=200, blank=True
    )
    postal_code = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=200, blank=True)
    country = CountryField(null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="attending_events"
    )

    search_indexer = SearchIndexer(
        ("A", "title"), ("B", "indexable_location"), ("C", "indexable_description"),
    )

    objects = EventManager()

    class Meta(Activity.Meta):
        indexes = Activity.Meta.indexes + [
            models.Index(fields=["starts"], name="event_starts_idx")
        ]

    def __str__(self):
        return self.title or self.location

    def clean(self):
        if self.ends and self.ends < self.starts:
            raise ValidationError(_("End date cannot be before start date"))

        if self.ends and self.ends.date() != self.starts.date() and self.repeats:
            raise ValidationError(_("End date must be same as start date if repeating"))

        if self.repeats_until and not self.repeats:
            raise ValidationError(
                _("Repeat until date cannot be set if not a repeating event")
            )

        if self.repeats_until and self.repeats_until < self.starts:
            raise ValidationError(_("Repeat until date cannot be before start date"))

    def get_domain(self):
        return get_domain(self.url) or ""

    def get_next_starts_with_tz(self):
        """Returns timezone-adjusted start time.

        Returns:
            datetime
        """
        return self.get_next_start_date().astimezone(self.timezone)

    def get_next_ends_with_tz(self):
        """Returns timezone-adjusted end time.

        Returns:
            datetime or None: returns None if ends is None.
        """
        if ends := self.get_next_end_date():
            return ends.astimezone(self.timezone)
        return None

    def get_location(self):
        """Returns a concatenated string of location fields.

        Will try to guess the correct format based on country.

        If any missing fields, will try to tidy up the string to remove
        any trailing commas and spaces.

        Returns:
            str
        """
        location = (
            self.get_address_format()
            .format(
                street_address=self.street_address,
                locality=self.locality,
                region=self.region,
                postcode=self.postal_code,
                country=self.country.name if self.country else "",
            )
            .replace("  ", " ")
            .replace(", ,", ", ")
            .strip()
        )
        # if location is just commas and spaces, return an empty string
        if location.replace(",", "").strip() == "":
            return ""

        if location.endswith(","):
            location = location[:-1]
        return smart_text(location)

    def get_full_location(self):
        """Includes venue if available along with location.

        Returns:
            str
        """
        return ", ".join(
            [smart_text(value) for value in [self.venue, self.get_location()] if value]
        )

    def get_geocoder_location(self):
        """Return a standard location for OSM lookup:
        - street address
        - locality
        - postal code
        - country name

        Returns:
            dict or None: returns None if any required fields are missing.
        """

        fields = {
            "street": self.street_address,
            "city": self.locality,
            "postalcode": self.postal_code,
            "country": self.country.name if self.country else None,
        }
        if not all(fields.values()):
            return None

        return fields

    @property
    def indexable_location(self):
        """Property required for search indexer. Just returns full location.
        """
        return self.get_full_location()

    def has_map(self):
        return all((self.latitude, self.longitude)) and not self.canceled

    def get_address_format(self):
        if not self.country:
            return self.DEFAULT_ADDRESS_FORMAT

        for codes, address_format in self.ADDRESS_FORMATS:
            if self.country.code in codes:
                return address_format

        return self.DEFAULT_ADDRESS_FORMAT

    def has_started(self):
        """If start date in past, unless still repeating.

        Returns:
            bool
        """
        if self.is_repeating():
            return False
        return self.starts < timezone.now()

    def has_ended(self):
        """If end date in past, unless still repeating.

        Returns:
            bool
        """
        if self.is_repeating():
            return False
        return self.ends < timezone.now()

    def get_next_start_date(self):
        """Returns next_date if repeating, otherwise starts.

        Note that this must be used with the with_next_date() QuerySet
        method.
        """
        if not self.is_repeating():
            return self.starts

        if not hasattr(self, "next_date"):
            raise AttributeError(
                "next_date not present: must be used with EventQuerySet.with_next_date()"
            )
        # ensure date/times preserved
        return self.next_date.replace(hour=self.starts.hour, minute=self.starts.minute)

    def get_next_end_date(self):

        """Returns the next_date plus ends time (must be same date as the start date)

        Note that this must be used with the with_next_date() QuerySet
        method.
        """

        if not self.ends or not self.is_repeating():
            return self.ends

        if not hasattr(self, "next_date"):
            raise AttributeError(
                "next_date not present: must be used with EventQuerySet.with_next_date()"
            )

        return self.ends.replace(
            day=self.next_date.day,
            month=self.next_date.month,
            year=self.next_date.year,
        )

    def is_repeating(self):
        """If has repeat option, and repeats_until is NULL or
        in future.

        Returns:
            bool
        """
        if not self.repeats:
            return False
        if self.repeats_until is None:
            return True
        return self.repeats_until > timezone.now()

    def repeats_daily(self):
        return self.repeats == self.RepeatChoices.DAILY

    def repeats_weekly(self):
        return self.repeats == self.RepeatChoices.WEEKLY

    def repeats_monthly(self):
        return self.repeats == self.RepeatChoices.MONTHLY

    def repeats_yearly(self):
        return self.repeats == self.RepeatChoices.YEARLY

    def is_attendable(self):
        """If event can be attended:
            - start date in future
            - not private
            - not canceled or deleted
        Returns:
            bool
        """
        return all(
            (
                self.published,
                not (self.deleted),
                not (self.canceled),
                not (self.has_started()),
            )
        )

    def matches_date(self, dt):
        """Checks if event has a date matching this date. Useful e.g.
        for scrolling through a list of dates.

        Args:
            dt (datetime)

        Returns:
            bool: if event occurs on this date (single or repeating)
        """
        exact_match = (
            self.starts.day == dt.day
            and self.starts.month == dt.month
            and self.starts.year == dt.year
        )

        # if non-repeating then must always be an exact match.
        if not self.is_repeating():
            return exact_match

        # matches IF:
        # 1) has already started repeating (dt > starts)
        # 2) now or dt < repeats_until
        # 3) dt matches the appropriate repeats criteria.

        if not exact_match and self.starts > dt:
            return False

        if self.repeats_until and (
            self.repeats_until < dt or self.repeats_until < timezone.now()
        ):
            return False

        if self.repeats == self.RepeatChoices.DAILY:
            return True

        if self.repeats == self.RepeatChoices.WEEKLY:
            return dt.weekday() == self.starts.weekday()

        if self.repeats == self.RepeatChoices.MONTHLY:
            return dt.day == 1

        if self.repeats == self.RepeatChoices.YEARLY:
            return dt.day == self.starts.day and dt.month == self.starts.month

        return False

    @dispatch
    def notify_on_attend(self, attendee):
        """Notifies owner (if not themselves the attendee) of attendance.
        Args:
            actor (User)

        Returns:
            list (List[Notification])
        """
        if attendee == self.owner:
            return None
        return self.make_notification(
            recipient=self.owner, actor=attendee, verb="attend"
        )

    @dispatch
    def notify_on_cancel(self, actor):
        """Notify all attendees of cancellation. Also notify the event
        owner if the actor is not the owner.

        Args:
            actor (User)

        Returns:
            list (List[Notification])
        """
        recipients = self.attendees.exclude(pk=actor.pk)
        if actor == self.owner:
            recipients = recipients.exclude(pk=self.owner.pk)
        else:
            recipients = recipients | get_user_model().objects.filter(pk=self.owner.pk)

        recipients = recipients.filter(
            membership__active=True, membership__community=self.community
        )

        return [
            self.make_notification(recipient=recipient, actor=actor, verb="cancel")
            for recipient in recipients
        ]

    def to_ical(self):
        """Returns iCalendar event object.

        Returns:
            Calendar
        """
        event = CalendarEvent()

        starts = self.get_next_starts_with_tz()

        event.add("dtstart", starts)
        event.add("dtstamp", starts)

        if ends := self.get_next_ends_with_tz():
            event.add("dtend", ends)

        event.add("summary", self.title)

        if location := self.get_full_location():
            event.add("location", location)

        if self.description:
            event.add("description", self.description.plaintext().splitlines())

        calendar = Calendar()
        calendar.add_component(event)
        return calendar.to_ical()
