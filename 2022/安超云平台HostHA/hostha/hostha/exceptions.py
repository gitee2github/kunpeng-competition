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

from oslo_utils import uuidutils
from .i18n import _


def wrap_keystone_exception(func):
    """Wrap keystone exceptions and throw Watcher specific exceptions."""
    @functools.wraps(func)
    def wrapped(*args, **kw):
        try:
            return func(*args, **kw)
        except Exception:
            raise
    return wrapped


class CloudultraError(Exception):
    code = "UNKNOWN_EXCEPTION"
    message = _("An unknown exception occurred")

    def __str__(self):
        return self.message

    def __init__(self, message=None, code=None, inject_error_id=False):
        self.uuid = uuidutils.generate_uuid()

        if code:
            self.code = code
        if message:
            self.message = message

        if inject_error_id:
            # Add Error UUID to the message if required
            self.message = (_('%(message)s\nError ID: %(id)s')
                            % {'message': self.message, 'id': self.uuid})

        super(CloudultraError, self).__init__(
            '%s: %s' % (self.code, self.message))


class NotFoundError(CloudultraError):
    code = "NOT_FOUND"
    message_template = _("Object '%s' is not found")

    # It could be a various property of object which was not found
    def __init__(self, value, message_template=None):
        self.value = value
        if message_template:
            formatted_message = message_template % value
        else:
            formatted_message = self.message_template % value

        super(NotFoundError, self).__init__(formatted_message)


class BadRequestError(CloudultraError):
    code = "BAD_REQUEST"
    message_template = _("Bad request")


class AuthError(CloudultraError):
    code = "AUTH_ERROR"
    message_template = _("Keystone Auth Error")


class CallNovaApiError(CloudultraError):
    code = "CALLNOVAAPI_ERROR"
    message_template = _("Call Nova Api Error")


class ValidationError(BadRequestError):
    code = "VALIDATION_ERROR"


class AlarmNotFoundError(NotFoundError):
    message_template = _("Alarm '%s' is not found")


class AlarmHistoryItemNotFoundError(NotFoundError):
    message_template = _("AlarmHistoryItem '%s' is not found")


class NoUniqueMatchException(CloudultraError):
    code = "NO_UNIQUE_MATCH"
    message_template = _(
        "Response {response} is not unique for this query {query}.")

    def __init__(self, response, query, message_template=None):
        template = message_template or self.message_template
        formatted_message = template.format(response=response, query=query)
        super(NoUniqueMatchException, self).__init__(formatted_message)


class NameAlreadyExistsException(BadRequestError):
    code = "NAME_ALREADY_EXISTS"
    message = _("Name already exists")


class ScheduleNotFoundError(NotFoundError):
    message_template = _("Schedule '%s' not found")


class ServiceNotFoundError(NotFoundError):
    message_template = _("Service '%s' not found")


class ScheduleHistoryItemNotFoundError(NotFoundError):
    message_template = _("ScheduleHistoryItem '%s' is not found")


class DBDuplicateEntry(CloudultraError):
    code = "DB_DUPLICATE_ENTRY"

    def __init__(self, e):
        message = (_("Duplicate entry for object %(object)s. "
                     "Failed on columns: %(columns)s")
                   % {"object": e.value, "columns": e.columns})
        super(DBDuplicateEntry, self).__init__(message)


class CreationFailed(CloudultraError):
    message = _("Object was not created")
    code = "CREATION_FAILED"


class DeletionFailed(CloudultraError):
    code = "DELETION_FAILED"
    message = _("Object was not deleted")


class IncorrectStateError(BadRequestError):
    message = _("The object is in an incorrect state")
    code = "INCORRECT_STATE_ERROR"


class TimeoutException(CloudultraError):
    code = "TIMEOUT"
    message_template = _("'%(operation)s' timed out after %(timeout)i "
                         "second(s)")

    def __init__(self, timeout, op_name=None, timeout_name=None):
        if op_name:
            op_name = _("Operation with name '%s'") % op_name
        else:
            op_name = _("Operation")
        formatted_message = self.message_template % {
            'operation': op_name, 'timeout': timeout}

        if timeout_name:
            desc = _("%(message)s and following timeout was violated: "
                     "%(timeout_name)s")
            formatted_message = desc % {
                'message': formatted_message, 'timeout_name': timeout_name}

        super(TimeoutException, self).__init__(formatted_message)


class Forbidden(CloudultraError):
    code = "FORBIDDEN"
    message = _("You are not authorized to complete this action")


class MalformedRequestBody(BadRequestError):
    code = "MALFORMED_REQUEST_BODY"
    message_template = _("Malformed message body: %(reason)s")

    def __init__(self, reason):
        formatted_message = self.message_template % {"reason": reason}
        super(MalformedRequestBody, self).__init__(formatted_message)


class QuotaException(BadRequestError):
    code = "QUOTA_ERROR"
    message_template = _("Quota exceeded for %(resource)s: "
                         "Requested %(requested)s, "
                         "but available %(available)s")

    def __init__(self, resource, requested, available):
        formatted_message = self.message_template % {
            'resource': resource,
            'requested': requested,
            'available': available}

        super(QuotaException, self).__init__(formatted_message)


class UpdateFailedException(CloudultraError):
    code = "UPDATE_FAILED"
    message_template = _("Object '%s' could not be updated")
    # Object was unable to be updated

    def __init__(self, value, message_template=None):
        if message_template:
            self.message_template = message_template

        formatted_message = self.message_template % value

        super(UpdateFailedException, self).__init__(formatted_message)


class ConfigurationError(CloudultraError):
    code = "CONFIGURATION_ERROR"
    message = _("The configuration has failed")


class EndpointNotFound(CloudultraError):
    code = "ENDPOINT_NOT_FOUND"

    def __init__(self, service_type, url_type, region=None):
        if region:
            message = ("%s endpoint of service %s in region %s not found"
                       % (url_type, service_type, region))
        else:
            message = "%s endpoint of service %s not found" % (url_type,
                                                               service_type)
        super(EndpointNotFound, self).__init__(message)


class EndpointNotFound2(CloudultraError):
    code = "ENDPOINT_NOT_FOUND"

    def __init__(self, service_id, interface, region=None):
        if region:
            message = ("%s endpoint of service %s in region %s not found"
                       % (interface, service_id, region))
        else:
            message = "%s endpoint of service %s not found" % (interface,
                                                               service_id)
        super(EndpointNotFound2, self).__init__(message)


class MultipleEndpointFound(CloudultraError):
    code = "MULTIPLE_ENDPOINT_FOUND"

    def __init__(self, service_id, interface, region=None):
        if region:
            message = ("Multiple %s endpoints of service %s in region %s found"
                       % (interface, service_id, region))
        else:
            message = ("Multiple %s endpoints of service %s found"
                       % (interface, region))
        super(MultipleEndpointFound, self).__init__(message)


class ServiceNotFound(NotFoundError):
    code = "SERVICE_NOT_FOUND"

    def __init__(self, service_name):
        message = "Service %s cloud not be found" % service_name
        super(NotFoundError, self).__init__(message)


class ProjectNotFound(NotFoundError):
    code = "PROJECT_NOT_FOUND"

    def __init__(self, project_id):
        message = "Project %s cloud not be found" % project_id
        super(NotFoundError, self).__init__(message)


class MultipleServiceFound(CloudultraError):
    code = "MULTIPLE_SERVICE_FOUND"

    def __init__(self, service_name):
        message = "Multiple instances of service %s was found" % service_name
        super(MultipleServiceFound, self).__init__(message)


class ResourceNotFound(CloudultraError):
    msg_fmt = _("The %(name)s resource %(id)s could not be found")


class AlreadyHaveValueERROR(CloudultraError):
    code = "ALREADY_HAVE_VALUE_ERROR"
    message = _("value is already %s")
