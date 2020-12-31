import datetime
import json
from typing import Iterator

"""Tests for `aws_session_recorder.lib.schema.user` package."""
from aws_session_recorder.lib.schema.role import Role, RolePolicy
from tests.test_base import *

role_name2 = role_name+"2"


def test_role(role, session):
    for key, value in role['Role'].items():
        if key == 'AssumeRolePolicyDocument':
            # TODO: Fix this edge case
            assert json.dumps(value) == json.dumps(json.loads(getattr(session.db.query(Role).all()[0], key)))
            continue
        assert value == getattr(session.db.query(Role).all()[0], key)


@pytest.fixture(scope='function')
def role2(iam) -> t.GetRoleResponseTypeDef:
    iam.create_role(RoleName=role_name2, AssumeRolePolicyDocument=test_policy)
    return iam.get_role(RoleName=role_name2)


def test_role2(session: Session, role, role2):
    assert session.db.query(Role).count() == 2
    assert role_name == session.db.query(Role).all()[0].RoleName
    assert role_name2 == session.db.query(Role).all()[1].RoleName


@pytest.fixture(scope='function')
def inline_role_policy(iam, role) -> t.GetRolePolicyResponseTypeDef:
    iam.put_role_policy(RoleName=role_name, PolicyName='test_policy', PolicyDocument=test_policy)
    return iam.get_role_policy(RoleName=role_name, PolicyName='test_policy')


def test_inline_role_policy(session, inline_role_policy: t.GetRolePolicyResponseTypeDef):
    assert inline_role_policy['PolicyName'] == session.db.query(RolePolicy).first().PolicyName


def test_inline_role_policy_by_role(session, inline_role_policy: t.GetRolePolicyResponseTypeDef):
    live_name = inline_role_policy['PolicyName']
    role: Role = session.db.query(Role).first()
    assert live_name == role.inline_policies[0].PolicyName


def test_inline_role_policy_document(session, inline_role_policy: t.GetRolePolicyResponseTypeDef):
    live_doc = json.dumps(inline_role_policy['PolicyDocument'])
    # TODO: Fix this edge case
    db_doc = json.dumps(json.loads(session.db.query(RolePolicy).first().PolicyDocument))
    assert live_doc == db_doc


