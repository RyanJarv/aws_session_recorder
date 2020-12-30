from typing import TYPE_CHECKING

from typing import List

import sqlalchemy as sa  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy_utils import JSONType  # type: ignore

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.base import Base

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()

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

