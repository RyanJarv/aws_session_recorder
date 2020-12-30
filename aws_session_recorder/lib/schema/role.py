import json
from typing import TYPE_CHECKING, Iterator, Any, Union

from typing import List

import sqlalchemy as sa  # type: ignore
from sqlalchemy_utils import JSONType  # type: ignore

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.identity import Identity

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()

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
