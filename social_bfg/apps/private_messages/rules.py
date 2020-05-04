# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import rules

# Social-BFG
from social_bfg.apps.communities.rules import is_member

rules.add_perm("private_messages.create_message", is_member)