import json
from typing import TYPE_CHECKING, Iterator, Any, Union

from typing import List

import sqlalchemy as sa  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy_utils import JSONType  # type: ignore

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.base import Base
from aws_session_recorder.lib.schema.policy import policy_attachments, UserPolicy

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()

group_membership = sa.Table('group_membership', Base.metadata,
                            sa.Column('user_id', sa.String, sa.ForeignKey('user.arn')),
                            sa.Column('group_id', sa.Integer, sa.ForeignKey('group.id')),
                            )


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

    users: List[Any] = relationship("User", back_populates="groups", secondary=group_membership)

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

class User(Identity):
    def __init__(self, resp: t.UserTypeDef):
        super().__init__(resp)

    __tablename__ = "user"

    UserName: str = sa.Column(sa.String, primary_key=True)
    UserId: str = sa.Column(sa.String)

    arn = sa.Column(sa.String, sa.ForeignKey('identity.Arn'))
    access_keys = relationship("AccessKey", back_populates="user")

    groups: List[Group] = relationship("Group", back_populates="users", secondary=group_membership)

    inline_policies: List[UserPolicy] = relationship("UserPolicy", cascade="all, delete-orphan", back_populates="user")

    __mapper_args__ = {
        'polymorphic_identity': 'user'
    }



class AccessKey(Base):
    __tablename__ = "access_key"

    def __init__(self, key: t.AccessKeyMetadataTypeDef):
        super().__init__(**key)

    id: int = sa.Column(sa.Integer, primary_key=True)

    UserName: str = sa.Column(sa.String, sa.ForeignKey('user.UserName'))
    AccessKeyId: str = sa.Column(sa.String)
    Status: dict = sa.Column(sa.String)
    CreateDate: str = sa.Column(sa.String)

    user: User = relationship("User", back_populates="access_keys")


class Role(Identity):
    __tablename__ = "role"

    def __init__(self, resp: t.GetRoleResponseTypeDef):
        # RoleLastUsed.LastUsedDate returns a datetime.datetime object, workaround this by serialize/deserializing
        # with default=str
        # TODO: better way to handle this without making RoleLastUsed a JSONType?
        if 'RoleLastUsed' in resp['Role']:
            resp['Role']['RoleLastUsed'] = json.loads(json.dumps(resp['Role']['RoleLastUsed'], default=str))

        super().__init__(resp["Role"])

    RoleName: str = sa.Column(sa.String, primary_key=True)
    RoleId: str = sa.Column(sa.String)
    AssumeRolePolicyDocument: dict = sa.Column(JSONType)
    MaxSessionDuration: int = sa.Column(sa.Integer)
    RoleLastUsed: dict = sa.Column(JSONType)

    arn = sa.Column(sa.String, sa.ForeignKey('identity.Arn'))
    __mapper_args__ = {
        'polymorphic_identity': 'role'
    }


class InstanceProfile(Identity):
    __tablename__ = "instance_profile"

    def __init__(self, resp: t.GetInstanceProfileResponseTypeDef):
        # TODO: handle datetime in role policy
        resp['InstanceProfile']['Roles'] = json.loads(json.dumps(resp['InstanceProfile']['Roles'], default=str))
        super().__init__(resp['InstanceProfile'])

    InstanceProfileName: str = sa.Column(sa.String, primary_key=True)
    InstanceProfileId: str = sa.Column(sa.String)
    AssumeRolePolicyDocument: dict = sa.Column(JSONType)

    # TODO Should reference a role
    Roles: List[dict] = sa.Column(JSONType)

    arn = sa.Column(sa.String, sa.ForeignKey('identity.Arn'))
    __mapper_args__ = {
        'polymorphic_identity': 'instance_profile'
    }
