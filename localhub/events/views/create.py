# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from localhub.activities.views.edit import ActivityCreateView


class EventCreateView(ActivityCreateView):
    def get_initial(self):
        initial = super().get_initial()
        initial["timezone"] = self.request.user.default_timezone
        return initial
