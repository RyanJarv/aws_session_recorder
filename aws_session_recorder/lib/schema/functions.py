import json
from typing import TYPE_CHECKING, Iterator

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.group import Group, GroupPolicy
from aws_session_recorder.lib.schema.role import Role, InstanceProfile, RolePolicy
from aws_session_recorder.lib.schema.policy import Policy, PolicyVersion, UserPolicyAttachments, RolePolicyAttachments, \
    GroupPolicyAttachments
from aws_session_recorder.lib.schema.user import User, AccessKey, UserPolicy

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()


def GetUser(req_params: dict, resp: t.GetUserResponseTypeDef):
    return User(resp['User'])


def ListUsers(req_params: dict, resp: t.ListUsersResponseTypeDef):
    for node in resp['Users']:
        yield User(node)


def GetGroup(req_params: dict, resp: t.GetGroupResponseTypeDef) -> Iterator[Group]:
    grp: Group = Group(resp['Group'])
    grp.users = [User(user) for user in resp['Users']]
    yield grp


def ListGroups(req_params: dict, resp: t.ListGroupsResponseTypeDef):
    for node in resp['Groups']:
        yield Group(node)


def ListAccessKeys(req_params: dict, resp: t.ListAccessKeysResponseTypeDef) -> Iterator[AccessKey]:
    for key in resp['AccessKeyMetadata']:
        yield AccessKey(key)


def ListUserPolicies(req_params: dict, resp: t.ListUserPoliciesResponseTypeDef):
    # UserName is only present in the req_params, merge with resp so we can correlate the list to a user
    for policy_name in resp['PolicyNames']:
        yield UserPolicy({'UserName': req_params['UserName'], 'PolicyName': policy_name})


def GetUserPolicy(req_params: dict, resp: t.GetUserPolicyResponseTypeDef):
    # This key actually does exist, tests will fail if we remove this
    if resp.get('ResponseMetadata'):  # type: ignore[misc]
        del resp['ResponseMetadata']  # type: ignore[misc]
    return UserPolicy(resp)


def GetRolePolicy(req_params: dict, resp: t.GetRolePolicyResponseTypeDef):
    # This key actually does exist, tests will fail if we remove this
    if resp.get('ResponseMetadata'):  # type: ignore[misc]
        del resp['ResponseMetadata']  # type: ignore[misc]
    return RolePolicy(resp)


def ListRolePolicies(req_params: dict, resp: t.ListRolePoliciesResponseTypeDef):
    # UserName is only present in the req_params, merge with resp so we can correlate the list to a user
    for policy_name in resp['PolicyNames']:
        yield RolePolicy({'RoleName': req_params['RoleName'], 'PolicyName': policy_name})


def GetGroupPolicy(req_params: dict, resp: t.GetGroupPolicyResponseTypeDef) -> GroupPolicy:
    # This key actually does exist, tests will fail if we remove this
    if resp.get('ResponseMetadata'):  # type: ignore[misc]
        del resp['ResponseMetadata']  # type: ignore[misc]
    return GroupPolicy(resp)


def ListGroupPolicies(req_params: dict, resp: t.ListGroupPoliciesResponseTypeDef):
    # UserName is only present in the req_params, merge with resp so we can correlate the list to a user
    for policy_name in resp['PolicyNames']:
        yield GroupPolicy({'GroupName': req_params['GroupName'], 'PolicyName': policy_name})


def GetPolicy(req_params: dict, resp: t.GetPolicyResponseTypeDef) -> Policy:
    return Policy(resp['Policy'])


def ListPolicies(req_params: dict, resp: t.ListPoliciesResponseTypeDef) -> Iterator[Policy]:
    for p in resp['Policies']:
        yield Policy(p)

def GetPolicyVersion(req_params: dict, resp: t.GetPolicyVersionResponseTypeDef):
    return PolicyVersion(resp['PolicyVersion'])


def ListPolicyVersions(req_params: dict, resp: t.ListPolicyVersionsResponseTypeDef):
    print(resp.keys())
    for version in resp['Versions']:
        PolicyVersion(version)


def GetInstanceProfile(req_params: dict, resp: t.GetInstanceProfileResponseTypeDef):
    # TODO: handle datetime in role policy
    resp['InstanceProfile']['Roles'] = json.loads(json.dumps(resp['InstanceProfile']['Roles'], default=str))
    return InstanceProfile(resp['InstanceProfile'])


def GetRole(req_params: dict, resp: t.GetRoleResponseTypeDef):
    # RoleLastUsed.LastUsedDate returns a datetime.datetime object, workaround this by serialize/deserializing
    # with default=str
    # TODO: better way to handle this without making RoleLastUsed a JSONType?
    if 'RoleLastUsed' in resp['Role']:
        resp['Role']['RoleLastUsed'] = json.loads(json.dumps(resp['Role']['RoleLastUsed'], default=str))

    return Role(resp["Role"])


def ListRoles(req_params: dict, resp: t.ListRolesResponseTypeDef):
    for node in resp['Roles']:
        yield Role(node)


def ListAttachedUserPolicies(req_params: dict, resp: t.ListAttachedUserPoliciesResponseTypeDef):
    for node in resp['AttachedPolicies']:
        node.update(req_params)
        yield Policy({'Arn': node['PolicyArn'], 'PolicyName': node['PolicyName']})
        yield UserPolicyAttachments(node)

def ListAttachedRolePolicies(req_params: dict, resp: t.ListAttachedRolePoliciesResponseTypeDef):
    for node in resp['AttachedPolicies']:
        node.update(req_params)
        yield Policy({'Arn': node['PolicyArn'], 'PolicyName': node['PolicyName']})
        yield RolePolicyAttachments(node)


def ListAttachedGroupPolicies(req_params: dict, resp: t.ListAttachedGroupPoliciesResponseTypeDef):
    for node in resp['AttachedPolicies']:
        node.update(req_params)
        yield Policy({'Arn': node['PolicyArn'], 'PolicyName': node['PolicyName']})
        yield GroupPolicyAttachments(node)

# TODO:
#   * get-account-authorization-details
#   * get-ssh-public-key
#   * list-entities-for-policy
#   * list-ssh-public-keys
#   * list-service-specific-credentials
#   * list-virtual-mfa-devices
#   * *-tags
#
#
#   * list-saml-providers
#   * list-server-certificates
#
#       o simulate-custom-policy ?
#       o simulate-principal-policy ?
#       * get-organizations-access-report?
#       * get-account-summary ?
#       * get-access-key-last-used ?
#
ApiCallMap = {
    'GetUser': GetUser,
    'ListUsers': ListUsers,
    'GetRole': GetRole,
    'ListRoles': ListRoles,
    'ListAttachedUserPolicies': ListAttachedUserPolicies,
    'ListAttachedRolePolicies': ListAttachedRolePolicies,
    'ListAttachedGroupPolicies': ListAttachedGroupPolicies,
    'GetUserPolicy': GetUserPolicy,
    'ListUserPolicies': ListUserPolicies,
    'ListPolicies': ListPolicies,
    'GetRolePolicy': GetRolePolicy,
    'ListRolePolicies': ListRolePolicies,
    'GetGroupPolicy': GetGroupPolicy,
    'ListGroupPolicies': ListGroupPolicies,
    'GetPolicy': GetPolicy,
    'GetPolicyVersion': GetPolicyVersion,
    'ListPolicyVersions': ListPolicyVersions,
    'GetInstanceProfile': GetInstanceProfile,
    'ListAccessKeys': ListAccessKeys,
    'GetGroup': GetGroup,
    'ListGroups': ListGroups,
}

