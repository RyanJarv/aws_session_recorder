from typing import TYPE_CHECKING, Dict, Union

from typing import List

import sqlalchemy as sa  # type: ignore
from sqlalchemy.orm import relationship
from sqlalchemy_utils import JSONType  # type: ignore

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.identity import Identity, InlinePolicy
from aws_session_recorder.lib.schema.policy import Policy

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()


class Role(Identity):
    __tablename__ = "role"

    RoleName: str = sa.Column(sa.String, primary_key=True)
    RoleId: str = sa.Column(sa.String)
    AssumeRolePolicyDocument: dict = sa.Column(JSONType)
    MaxSessionDuration: int = sa.Column(sa.Integer)
    RoleLastUsed: dict = sa.Column(JSONType)
    Description: str = sa.Column(sa.String)

    arn = sa.Column(sa.String, sa.ForeignKey('identity.Arn'))

    attached_policies: List['Policy'] = relationship('RolePolicyAttachments', back_populates='role')
    inline_policies: List['RolePolicy'] = relationship("RolePolicy", cascade="all, delete-orphan", back_populates="role")

    __mapper_args__ = {
        'polymorphic_identity': 'role'
    }


class InstanceProfile(Identity):
    __tablename__ = "instance_profile"

    InstanceProfileName: str = sa.Column(sa.String, primary_key=True)
    InstanceProfileId: str = sa.Column(sa.String)
    AssumeRolePolicyDocument: dict = sa.Column(JSONType)

    # TODO Should reference a role
    Roles: List[dict] = sa.Column(JSONType)

    arn = sa.Column(sa.String, sa.ForeignKey('identity.Arn'))
    __mapper_args__ = {
        'polymorphic_identity': 'instance_profile'
    }


class RolePolicy(InlinePolicy):
    __tablename__ = "role_policy"

    def __init__(self, resp: Union[t.GetRolePolicyResponseTypeDef, Dict]):
        super().__init__(**resp)

    policy_name = sa.Column(sa.String, sa.ForeignKey('inline_policy.PolicyName'), primary_key=True)
    RoleName = sa.Column(sa.String, sa.ForeignKey('role.RoleName'))

    role: 'List[Role]' = relationship("Role", back_populates="inline_policies")

    __mapper_args__ = {
        'polymorphic_identity': 'role'
    }
