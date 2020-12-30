import json
from typing import TYPE_CHECKING, Iterator, Union

from typing import List

import sqlalchemy as sa  # type: ignore
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy_utils import JSONType  # type: ignore

from aws_session_recorder.lib.helpers import AlwaysDoNothing

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()

Base: DeclarativeMeta = declarative_base()


policy_attachments = sa.Table('policy_attachments', Base.metadata,
                              sa.Column('identity_id', sa.Integer, sa.ForeignKey('identity.id')),
                              sa.Column('policy_id', sa.Integer, sa.ForeignKey('policy.id')),
                              )


class PolicyVersion(Base):
    __tablename__ = "policy_version"

    def __init__(self, resp: t.GetPolicyVersionResponseTypeDef):
        super().__init__(**resp['PolicyVersion'])

    VersionId: str = sa.Column(sa.String, primary_key=True)
    PolicyVersion: str = sa.Column(sa.String)
    Document: dict = sa.Column(JSONType)
    IsDefaultVersion: bool = sa.Column(sa.Boolean)
    CreateDate: str = sa.Column(sa.String)  # TODO: should be datetime object

    policy_id: int = sa.Column(sa.Integer, sa.ForeignKey('policy.id'))
    policy = relationship("Policy", back_populates="versions")


class Policy(Base):
    __tablename__ = "policy"

    def __init__(self, resp: t.GetPolicyResponseTypeDef):
        super().__init__(**resp['Policy'])

    id = sa.Column(sa.Integer, primary_key=True)
    PolicyName = sa.Column(sa.String)
    PolicyId = sa.Column(sa.String)
    Arn = sa.Column(sa.String)
    Path = sa.Column(sa.String)
    DefaultVersionId = sa.Column(sa.String)
    AttachmentCount = sa.Column(sa.String)
    PermissionsBoundaryUsageCount = sa.Column(sa.Integer)
    IsAttachable = sa.Column(sa.Boolean)
    Description = sa.Column(sa.String)
    CreateDate = sa.Column(sa.String)
    UpdateDate = sa.Column(sa.String)

    attached_to = relationship("Identity", secondary=policy_attachments, back_populates="attached_policies")
    versions: List[PolicyVersion] = relationship("PolicyVersion", back_populates="policy")


class Identity(Base):
    def __init__(self, resp):
        super().__init__(**resp)

    __tablename__ = "identity"

    id: int = sa.Column(sa.Integer, unique=True)

    Path: str = sa.Column(sa.String)
    Arn: str = sa.Column(sa.String, primary_key=True)
    CreateDate: str = sa.Column(sa.String)
    Tags: List[t.TagTypeDef] = sa.Column(JSONType)

    attached_policies = relationship("Policy", secondary=policy_attachments)

    type: str = sa.Column(sa.String(20))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'identity'
    }


group_membership = sa.Table('group_membership', Base.metadata,
                            sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')),
                            sa.Column('group_id', sa.Integer, sa.ForeignKey('group.id')),
                            )


def GetUserPolicy(resp: t.GetUserPolicyResponseTypeDef):
    # This key actually does exist, tests will fail if we remove this
    if resp.get('ResponseMetadata'):  # type: ignore[misc]
        del resp['ResponseMetadata']  # type: ignore[misc]
    return UserPolicy(resp)


class UserPolicy(Base):
    __tablename__ = "user_policy"

    def __init__(self, resp: t.GetUserPolicyResponseTypeDef):
        super().__init__(**resp)

    id = sa.Column(sa.Integer, primary_key=True)
    UserName = sa.Column(sa.String, sa.ForeignKey('user.UserName'))
    PolicyName = sa.Column(sa.String)
    PolicyDocument = sa.Column(JSONType)

    #user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    user = relationship("User", back_populates="inline_policies")


def GetUser(resp: t.GetUserResponseTypeDef):
    return User(resp['User'])


class User(Identity):
    def __init__(self, resp: t.UserTypeDef):
        super().__init__(resp)

    __tablename__ = "user"

    UserName: str = sa.Column(sa.String, primary_key=True)
    UserId: str = sa.Column(sa.String)

    id = sa.Column(sa.Integer, sa.ForeignKey('identity.Arn'))
    access_keys = relationship("AccessKey", back_populates="user")

    groups = relationship("Group", back_populates="users", secondary=group_membership)

    inline_policies: UserPolicy = relationship("UserPolicy", cascade="all, delete-orphan", back_populates="user")

    __mapper_args__ = {
        'polymorphic_identity': 'user'
    }


class Role(Identity):
    __tablename__ = "role"

    def __init__(self, resp: t.GetRoleResponseTypeDef):
        # RoleLastUsed.LastUsedDate returns a datetime.datetime object, workaround this by serialize/deserializing
        # with default=str
        # TODO: better way to handle this without making RoleLastUsed a JSONType?
        if 'RoleLastUsed' in resp['Role']:
            resp['Role']['RoleLastUsed'] = json.loads(json.dumps(resp['Role']['RoleLastUsed'], default=str))

        super().__init__(resp["Role"])

    RoleName: str = sa.Column(sa.String)
    RoleId: str = sa.Column(sa.String)
    AssumeRolePolicyDocument: dict = sa.Column(JSONType)
    MaxSessionDuration: int = sa.Column(sa.Integer)
    RoleLastUsed: dict = sa.Column(JSONType)

    id = sa.Column(sa.Integer, sa.ForeignKey('identity.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'role'
    }


class InstanceProfile(Identity):
    __tablename__ = "instance_profile"

    def __init__(self, resp: t.GetInstanceProfileResponseTypeDef):
        # TODO: handle datetime in role policy
        resp['InstanceProfile']['Roles'] = json.loads(json.dumps(resp['InstanceProfile']['Roles'], default=str))
        super().__init__(resp['InstanceProfile'])

    InstanceProfileName: str = sa.Column(sa.String)
    InstanceProfileId: str = sa.Column(sa.String)
    AssumeRolePolicyDocument: dict = sa.Column(JSONType)

    # TODO Should reference a role
    Roles: List[dict] = sa.Column(JSONType)

    id = sa.Column(sa.Integer, sa.ForeignKey('identity.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'instance_profile'
    }


class AccessKey(Base):
    __tablename__ = "access_key"

    def __init__(self, key: t.AccessKeyTypeDef):
        super().__init__(**key)

    id: int = sa.Column(sa.Integer, primary_key=True)

    UserName: str = sa.Column(sa.String, sa.ForeignKey('user.UserName'))
    AccessKeyId: str = sa.Column(sa.String)
    Status: dict = sa.Column(sa.String)
    CreateDate: str = sa.Column(sa.String)

    user = relationship("User", back_populates="access_keys")


def ListAccessKeys(resp: t.ListAccessKeysResponseTypeDef) -> Iterator[AccessKey]:
    for key in resp['AccessKeyMetadata']:
        yield AccessKey(key)


class Group(Base):
    __tablename__ = "group"

    def __init__(self, key: t.GroupTypeDef):
        super().__init__(**key)

    id: int = sa.Column(sa.Integer, primary_key=True)

    Path: str = sa.Column(sa.String)
    GroupName: str = sa.Column(sa.String)
    GroupId: str = sa.Column(sa.String)
    Arn: dict = sa.Column(sa.String)
    CreateDate: str = sa.Column(sa.String)

    users = relationship("User", back_populates="groups", secondary=group_membership)


def GetGroup(resp: t.GetGroupResponseTypeDef) -> Iterator[Union[Group, User]]:
    yield Group(resp['Group'])
    for user in resp['Users']:
        yield User(user)


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
