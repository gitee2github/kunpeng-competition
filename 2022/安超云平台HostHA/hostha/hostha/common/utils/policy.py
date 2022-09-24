# Copyright (c) 2016 ChinaC Inc.

from oslo_policy import policy
from oslo_config import cfg


ENFORCER = None


def setup_policy():
    global ENFORCER

    if not ENFORCER:
        ENFORCER = policy.Enforcer(cfg.CONF)


def enforce(rule, target, creds, do_raise=False, exc=None, *args, **kwargs):
    return ENFORCER.enforce(rule, target, creds, do_raise=do_raise, exc=exc,
                            *args, **kwargs)


def check_is_admin(ctx):
    setup_policy()
    # the target is user-self
    credentials = ctx.to_dict()
    target = credentials
    return ENFORCER.enforce('context_is_admin', target, credentials)
