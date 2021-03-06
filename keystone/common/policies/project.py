# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_log import versionutils
from oslo_policy import policy

from keystone.common.policies import base

SYSTEM_READER_OR_DOMAIN_READER_OR_PROJECT_USER = (
    '(' + base.SYSTEM_READER + ') or '
    '(role:reader and domain_id:%(target.project.domain_id)s) or '
    'project_id:%(target.project.id)s'
)

# This policy is only written to be used to protect the
# /v3/users/{user_id}/projects API. It should not be used to protect
# /v3/project APIs because the target information contained in the last check
# is specific to user targets from the user id passed in the
# /v3/users/{user_id}/project path.
SYSTEM_READER_OR_DOMAIN_READER_OR_OWNER = (
    # System reader policy
    '(' + base.SYSTEM_READER + ') or '
    # Domain reader policy
    '(role:reader and domain_id:%(target.user.domain_id)s) or '
    # User accessing the API with a token they've obtained, matching
    # the context user_id to the target user id.
    'user_id:%(target.user.id)s'
)

SYSTEM_READER_OR_DOMAIN_READER = (
    '(' + base.SYSTEM_READER + ') or '
    '(role:reader and domain_id:%(target.domain_id)s)'
)

deprecated_list_projects = policy.DeprecatedRule(
    name=base.IDENTITY % 'list_projects',
    check_str=base.RULE_ADMIN_REQUIRED
)
deprecated_get_project = policy.DeprecatedRule(
    name=base.IDENTITY % 'get_project',
    check_str=base.RULE_ADMIN_OR_TARGET_PROJECT
)
deprecated_list_user_projects = policy.DeprecatedRule(
    name=base.IDENTITY % 'list_user_projects',
    check_str=base.RULE_ADMIN_OR_OWNER
)
deprecated_create_project = policy.DeprecatedRule(
    name=base.IDENTITY % 'create_project',
    check_str=base.RULE_ADMIN_REQUIRED
)
deprecated_update_project = policy.DeprecatedRule(
    name=base.IDENTITY % 'update_project',
    check_str=base.RULE_ADMIN_REQUIRED
)
deprecated_delete_project = policy.DeprecatedRule(
    name=base.IDENTITY % 'delete_project',
    check_str=base.RULE_ADMIN_REQUIRED
)

DEPRECATED_REASON = """
As of the Stein release, the project API understands how to handle
system-scoped tokens in addition to project and domain tokens, making the API
more accessible to users without compromising security or manageability for
administrators. The new default policies for this API account for these changes
automatically.
"""

project_policies = [
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'get_project',
        check_str=SYSTEM_READER_OR_DOMAIN_READER_OR_PROJECT_USER,
        scope_types=['system', 'domain', 'project'],
        description='Show project details.',
        operations=[{'path': '/v3/projects/{project_id}',
                     'method': 'GET'}],
        deprecated_rule=deprecated_get_project,
        deprecated_reason=DEPRECATED_REASON,
        deprecated_since=versionutils.deprecated.STEIN),
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'list_projects',
        check_str=SYSTEM_READER_OR_DOMAIN_READER,
        # FIXME(lbragstad): Project administrators should be able to list
        # projects they administer or possibly their children.  Until keystone
        # is smart enough to handle those cases, keep scope_types set to
        # 'system' and 'domain'.
        scope_types=['system', 'domain'],
        description='List projects.',
        operations=[{'path': '/v3/projects',
                     'method': 'GET'}],
        deprecated_rule=deprecated_list_projects,
        deprecated_reason=DEPRECATED_REASON,
        deprecated_since=versionutils.deprecated.STEIN),
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'list_user_projects',
        check_str=SYSTEM_READER_OR_DOMAIN_READER_OR_OWNER,
        scope_types=['system', 'domain', 'project'],
        description='List projects for user.',
        operations=[{'path': '/v3/users/{user_id}/projects',
                     'method': 'GET'}],
        deprecated_rule=deprecated_list_user_projects,
        deprecated_reason=DEPRECATED_REASON,
        deprecated_since=versionutils.deprecated.STEIN),
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'create_project',
        check_str=base.SYSTEM_ADMIN,
        # FIXME(lbragstad): System administrators should be able to create
        # projects anywhere in the deployment. Domain administrators should
        # only be able to create projects within their domain. Project
        # administrators should only be able to create children projects of the
        # project they administer. Until keystone is smart enough to handle
        # those checks in code, keep this as a system-level operation for
        # backwards compatibility.
        scope_types=['system'],
        description='Create project.',
        operations=[{'path': '/v3/projects',
                     'method': 'POST'}],
        deprecated_rule=deprecated_create_project,
        deprecated_reason=DEPRECATED_REASON,
        deprecated_since=versionutils.deprecated.STEIN),
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'update_project',
        check_str=base.SYSTEM_ADMIN,
        # FIXME(lbragstad): See the above comment for create_project as to why
        # this is limited to only system-scope.
        scope_types=['system'],
        description='Update project.',
        operations=[{'path': '/v3/projects/{project_id}',
                     'method': 'PATCH'}],
        deprecated_rule=deprecated_update_project,
        deprecated_reason=DEPRECATED_REASON,
        deprecated_since=versionutils.deprecated.STEIN),
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'delete_project',
        check_str=base.SYSTEM_ADMIN,
        # FIXME(lbragstad): See the above comment for create_project as to why
        # this is limited to only system-scope.
        scope_types=['system'],
        description='Delete project.',
        operations=[{'path': '/v3/projects/{project_id}',
                     'method': 'DELETE'}],
        deprecated_rule=deprecated_delete_project,
        deprecated_reason=DEPRECATED_REASON,
        deprecated_since=versionutils.deprecated.STEIN),
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'list_project_tags',
        check_str=base.RULE_ADMIN_OR_TARGET_PROJECT,
        # FIXME(lbragstad): We need to make sure we check the project in the
        # token scope when authorizing APIs for project tags. System
        # administrators should be able to tag any project with anything.
        # Domain administrators should only be able to tag projects within
        # their domain. Project administrators should only be able to tag their
        # project. Until we have support for these cases in code and tested, we
        # should keep scope_types commented out.
        # scope_types=['system', 'project'],
        description='List tags for a project.',
        operations=[{'path': '/v3/projects/{project_id}/tags',
                     'method': 'GET'},
                    {'path': '/v3/projects/{project_id}/tags',
                     'method': 'HEAD'}]),
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'get_project_tag',
        check_str=base.RULE_ADMIN_OR_TARGET_PROJECT,
        # FIXME(lbragstad): See the above comments as to why this is commented
        # out.
        # scope_types=['system', 'project'],
        description='Check if project contains a tag.',
        operations=[{'path': '/v3/projects/{project_id}/tags/{value}',
                     'method': 'GET'},
                    {'path': '/v3/projects/{project_id}/tags/{value}',
                     'method': 'HEAD'}]),
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'update_project_tags',
        check_str=base.RULE_ADMIN_REQUIRED,
        # FIXME(lbragstad): See the above comment for create_project as to why
        # this is limited to only system-scope.
        scope_types=['system'],
        description='Replace all tags on a project with the new set of tags.',
        operations=[{'path': '/v3/projects/{project_id}/tags',
                     'method': 'PUT'}]),
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'create_project_tag',
        check_str=base.RULE_ADMIN_REQUIRED,
        # FIXME(lbragstad): See the above comment for create_project as to why
        # this is limited to only system-scope.
        scope_types=['system'],
        description='Add a single tag to a project.',
        operations=[{'path': '/v3/projects/{project_id}/tags/{value}',
                     'method': 'PUT'}]),
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'delete_project_tags',
        check_str=base.RULE_ADMIN_REQUIRED,
        # FIXME(lbragstad): See the above comment for create_project as to why
        # this is limited to only system-scope.
        scope_types=['system'],
        description='Remove all tags from a project.',
        operations=[{'path': '/v3/projects/{project_id}/tags',
                     'method': 'DELETE'}]),
    policy.DocumentedRuleDefault(
        name=base.IDENTITY % 'delete_project_tag',
        check_str=base.RULE_ADMIN_REQUIRED,
        # FIXME(lbragstad): See the above comment for create_project as to why
        # this is limited to only system-scope.
        scope_types=['system'],
        description='Delete a specified tag from project.',
        operations=[{'path': '/v3/projects/{project_id}/tags/{value}',
                     'method': 'DELETE'}])
]


def list_rules():
    return project_policies
