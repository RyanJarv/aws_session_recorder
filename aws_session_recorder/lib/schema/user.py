import json
from typing import TYPE_CHECKING, Iterator, Any, Union

from typing import List

import sqlalchemy as sa  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy_utils import JSONType  # type: ignore

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.base import Base
from aws_session_recorder.lib.schema.group import Group, group_membership
from aws_session_recorder.lib.schema.identity import Identity

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()


class UserPolicy(Base):
    __tablename__ = "user_policy"

    def __init__(self, resp: t.GetUserPolicyResponseTypeDef):
        super().__init__(**resp)

    id = sa.Column(sa.Integer, primary_key=True)
    UserName = sa.Column(sa.String, sa.ForeignKey('user.UserName'))
    PolicyName = sa.Column(sa.String)
    PolicyDocument = sa.Column(JSONType)

    #user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    user: 'List[User]' = relationship("User", back_populates="inline_policies")

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

