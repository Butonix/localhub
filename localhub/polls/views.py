# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.forms import inlineformset_factory
from django.utils.functional import cached_property
from rules.contrib.views import PermissionRequiredMixin
from vanilla import GenericModelView

from localhub.activities.views.detail import ActivityDetailView
from localhub.activities.views.form import ActivityCreateView, ActivityUpdateView
from localhub.activities.views.list import ActivityListView
from localhub.communities.views import CommunityRequiredMixin

from .models import Answer, Poll

AnswersFormSet = inlineformset_factory(
    Poll,
    Answer,
    fields=("description",),
    extra=4,
    max_num=4,
    min_num=2,
    labels={"description": ""},
)


class PollQuerySetMixin:
    def get_queryset(self):
        return super().get_queryset().with_answers()


class PollCreateView(ActivityCreateView):
    model = Poll

    @cached_property
    def answers_formset(self):
        if self.request.method == "POST":
            return AnswersFormSet(self.request.POST)
        return AnswersFormSet()

    def form_valid(self, form):
        if not self.answers_formset.is_valid():
            return self.form_invalid(form)
        response = super().form_valid(form)
        self.answers_formset.instance = self.object
        self.answers_formset.save()
        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["answers_formset"] = self.answers_formset
        return data


class PollUpdateView(ActivityUpdateView):
    @cached_property
    def answers_formset(self):
        if self.request.method == "POST":
            return AnswersFormSet(self.request.POST, instance=self.object)
        return AnswersFormSet(instance=self.object)

    def form_valid(self, form):
        if not self.answers_formset.is_valid():
            return self.form_invalid(form)
        response = super().form_valid(form)
        self.answers_formset.save()
        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["answers_formset"] = self.answers_formset
        return data


class PollDetailView(PollQuerySetMixin, ActivityDetailView):
    ...


class PollListView(PollQuerySetMixin, ActivityListView):
    ...


class AnswerVoteView(
    PermissionRequiredMixin, CommunityRequiredMixin, GenericModelView,
):

    permission_required = "polls.vote"
    template_name = "polls/includes/answers.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.object = self.get_object()

    def get_permission_object(self):
        return self.object.poll

    def get_queryset(self):
        return Answer.objects.filter(
            poll__community=self.request.community
        ).select_related("poll", "poll__community")

    def post(self, request, *args, **kwargs):
        has_voted_before = False
        for voted in Answer.objects.filter(
            voters=self.request.user, poll=self.object.poll
        ):
            voted.voters.remove(self.request.user)
            has_voted_before = True

        self.object.voters.add(self.request.user)

        if not has_voted_before:
            self.object.poll.notify_on_vote(self.request.user)

        poll = Poll.objects.with_answers().get(pk=self.object.poll.id)
        return self.render_to_response({"object": poll, "object_type": "poll"})


answer_vote_view = AnswerVoteView.as_view()
