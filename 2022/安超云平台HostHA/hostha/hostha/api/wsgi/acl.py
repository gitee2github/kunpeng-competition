# Copyright (c) 2021 Archeros Inc.
# hostha is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the
# Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import functools

from hostha import context
from hostha import exceptions
from hostha.common.utils import policy


def enforce(rule):
    def decorator(func):
        @functools.wraps(func)
        def handler(*args, **kwargs):
            ctx = context.ctx()
            target = {'tenant_id': ctx.tenant_id,
                      'user_id': ctx.user_id}
            policy.enforce(rule, target, ctx.to_dict(),
                           do_raise=True,
                           exc=exceptions.Forbidden)
            return func(*args, **kwargs)
        return handler

    return decorator
