import json
from typing import TYPE_CHECKING, Iterator, Any, Union

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.group import Group, GroupPolicy
from aws_session_recorder.lib.schema.role import Role, InstanceProfile, RolePolicy
from aws_session_recorder.lib.schema.policy import Policy, PolicyVersion
from aws_session_recorder.lib.schema.user import User, AccessKey, UserPolicy

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()


def GetUser(resp: t.GetUserResponseTypeDef):
    return User(resp['User'])


def ListUsers(resp: t.ListUsersResponseTypeDef):
    for node in resp['Users']:
        yield User(node)


def GetGroup(resp: t.GetGroupResponseTypeDef) -> Iterator[Group]:
    grp: Group = Group(resp['Group'])
    grp.users = [User(user) for user in resp['Users']]
    yield grp


def ListGroups(resp: t.ListGroupsResponseTypeDef):
    for node in resp['Groups']:
        yield Group(node)


def ListAccessKeys(resp: t.ListAccessKeysResponseTypeDef) -> Iterator[AccessKey]:
    for key in resp['AccessKeyMetadata']:
        yield AccessKey(key)


def GetUserPolicy(resp: t.GetUserPolicyResponseTypeDef):
    # This key actually does exist, tests will fail if we remove this
    if resp.get('ResponseMetadata'):  # type: ignore[misc]
        del resp['ResponseMetadata']  # type: ignore[misc]
    return UserPolicy(resp)

def GetRolePolicy(resp: t.GetRolePolicyResponseTypeDef):
    # This key actually does exist, tests will fail if we remove this
    if resp.get('ResponseMetadata'):  # type: ignore[misc]
        del resp['ResponseMetadata']  # type: ignore[misc]
    return RolePolicy(resp)


def GetGroupPolicy(resp: t.GetGroupPolicyResponseTypeDef) -> GroupPolicy:
    # This key actually does exist, tests will fail if we remove this
    if resp.get('ResponseMetadata'):  # type: ignore[misc]
        del resp['ResponseMetadata']  # type: ignore[misc]
    return GroupPolicy(resp)


def GetPolicy(resp: t.GetPolicyResponseTypeDef) -> Policy:
    return Policy(resp['Policy'])


def ListPolicies(resp: t.ListPoliciesResponseTypeDef) -> Iterator[Policy]:
    for p in resp['Policies']:
        yield Policy(p)

def GetPolicyVersion(resp: t.GetPolicyVersionResponseTypeDef):
    return PolicyVersion(resp['PolicyVersion'])


def GetInstanceProfile(resp: t.GetInstanceProfileResponseTypeDef):
    # TODO: handle datetime in role policy
    resp['InstanceProfile']['Roles'] = json.loads(json.dumps(resp['InstanceProfile']['Roles'], default=str))
    return InstanceProfile(resp['InstanceProfile'])


def GetRole(resp: t.GetRoleResponseTypeDef):
    # RoleLastUsed.LastUsedDate returns a datetime.datetime object, workaround this by serialize/deserializing
    # with default=str
    # TODO: better way to handle this without making RoleLastUsed a JSONType?
    if 'RoleLastUsed' in resp['Role']:
        resp['Role']['RoleLastUsed'] = json.loads(json.dumps(resp['Role']['RoleLastUsed'], default=str))

    return Role(resp["Role"])


def ListRoles(resp: t.ListRolesResponseTypeDef):
    for node in resp['Roles']:
        yield Role(node)



ApiCallMap = {
    'GetUser': GetUser,
    'ListUsers': ListUsers,
    'GetRole': GetRole,
    'ListRoles': ListRoles,
    'GetUserPolicy': GetUserPolicy,
    'ListPolicies': ListPolicies,
    'GetRolePolicy': GetRolePolicy,
    'GetGroupPolicy': GetGroupPolicy,
    'GetPolicy': GetPolicy,
    'GetPolicyVersion': GetPolicyVersion,
    'GetInstanceProfile': GetInstanceProfile,
    'ListAccessKeys': ListAccessKeys,
    'GetGroup': GetGroup,
    'ListGroups': ListGroups,
}

