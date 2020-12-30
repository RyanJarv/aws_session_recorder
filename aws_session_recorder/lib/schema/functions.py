from typing import TYPE_CHECKING, Iterator, Any, Union

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.group import Group
from aws_session_recorder.lib.schema.role import Role, InstanceProfile
from aws_session_recorder.lib.schema.policy import Policy, PolicyVersion
from aws_session_recorder.lib.schema.user import User, AccessKey, UserPolicy

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()

def GetUser(resp: t.GetUserResponseTypeDef):
    return User(resp['User'])


def GetGroup(resp: t.GetGroupResponseTypeDef) -> Iterator[Union[Group, User]]:
    grp: Group = Group(resp['Group'])
    grp.users = [User(user) for user in resp['Users']]
    yield grp


def ListAccessKeys(resp: t.ListAccessKeysResponseTypeDef) -> Iterator[AccessKey]:
    for key in resp['AccessKeyMetadata']:
        yield AccessKey(key)


def GetUserPolicy(resp: t.GetUserPolicyResponseTypeDef):
    # This key actually does exist, tests will fail if we remove this
    if resp.get('ResponseMetadata'):  # type: ignore[misc]
        del resp['ResponseMetadata']  # type: ignore[misc]
    return UserPolicy(resp)


ApiCallMap = {
    'GetUser': GetUser,
    'GetRole': Role,
    'GetUserPolicy': GetUserPolicy,
    'GetPolicy': Policy,
    'GetPolicyVersion': PolicyVersion,
    'GetInstanceProfile': InstanceProfile,
    'ListAccessKeys': ListAccessKeys,
    'GetGroup': GetGroup,
}

