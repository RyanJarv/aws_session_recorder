"""Tests for `aws_session_recorder.lib.schema.user` package."""
import typing

from aws_session_recorder.lib import Session
from aws_session_recorder.lib.schema.role import InstanceProfile

if typing.TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore


def test_instance_profile(session: Session, instance_profile: t.GetInstanceProfileResponseTypeDef):
    assert instance_profile['InstanceProfile']['Arn'] == session.db.query(InstanceProfile).first().Arn


# #TODO: Unsure what the best way to populate role's off this data is right now
# def test_instance_profile_role(session: Session, instance_profile: t.GetInstanceProfileResponseTypeDef):
#     assert instance_profile['InstanceProfile']['Roles'][0]['Arn'] == session.db.query(Role).first().Arn
