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

from oslo_utils import reflection

from hostha import exceptions as ex
from hostha.common.utils import api as u
from hostha.common.utils import api_validator
from hostha.i18n import _


def _get_path(path):
    if path:
        path_string = path[0]
        for x in path[1:]:
            path_string += '[%s]' % str(x)
        return path_string + ': '
    return ''


def _generate_error(errors):
    message = [_get_path(list(e.path)) + e.message for e in errors]
    if message:
        return ex.CloudultraError('\n'.join(message), "VALIDATION_ERROR")


# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2013 Mirantis Inc.

def validate(schema, *validators):
    def decorator(func):
        @functools.wraps(func)
        def handler(*args, **kwargs):
            request_data = u.request_data()
            try:
                if schema:
                    validator = api_validator.ApiValidator(schema)
                    errors = validator.iter_errors(request_data)
                    error = _generate_error(errors)
                    if error:
                        return u.bad_request(error)
                if validators:
                    for validator in validators:
                        validator(**kwargs)
            except ex.CloudultraError as e:
                return u.bad_request(e)
            except Exception as e:
                return u.internal_error(
                    500, "Error occurred during validation", e)

            return func(*args, **kwargs)

        return handler

    return decorator


def check_exists(get_func, *id_prop, **get_args):
    def decorator(func):
        @functools.wraps(func)
        def handler(*args, **kwargs):
            if id_prop and not get_args:
                get_args['id'] = id_prop[0]

            if 'marker' in id_prop:
                if 'marker' not in u.get_request_args():
                    return func(*args, **kwargs)
                kwargs['marker'] = u.get_request_args()['marker']

            get_kwargs = {}
            for get_arg in get_args:
                get_kwargs[get_arg] = kwargs[get_args[get_arg]]

            obj = None
            try:
                obj = get_func(**get_kwargs)
            except Exception as e:
                cls_name = reflection.get_class_name(e, fully_qualified=False)
                if 'notfound' not in cls_name.lower():
                    raise e
            if obj is None:
                e = ex.NotFoundError(get_kwargs,
                                     _('Object with %s not found'))
                return u.not_found(e)
            if 'marker' in kwargs:
                del(kwargs['marker'])
            return func(*args, **kwargs)

        return handler

    return decorator
