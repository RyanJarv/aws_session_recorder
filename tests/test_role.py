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
    iam.create_role(RoleName=role_name2, AssumeRolePolicyDocument=test_policy_doc)
    return iam.get_role(RoleName=role_name2)


def test_role2(session: Session, role, role2):
    assert session.db.query(Role).count() == 2
    assert role_name == session.db.query(Role).all()[0].RoleName
    assert role_name2 == session.db.query(Role).all()[1].RoleName


@pytest.fixture(scope='function')
def list_roles(session: Session, iam: IAMClient) -> t.ListUsersResponseTypeDef:
    assert 0 == session.db.query(Role).count()
    iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=test_policy_doc)
    iam.create_role(RoleName=role_name2, AssumeRolePolicyDocument=test_policy_doc)
    return iam.list_roles()


def test_list_roles(session: Session, list_roles: t.ListRolesResponseTypeDef):
    assert len(list_roles['Roles']) == session.db.query(Role).count()
    assert len(list_roles['Roles']) == 2

@pytest.fixture(scope='function')
def inline_role_policy_list(iam: IAMClient, role: t.GetRoleResponseTypeDef) -> t.ListRolePoliciesResponseTypeDef:
    iam.put_role_policy(RoleName=role_name, PolicyName='test_policy', PolicyDocument=test_policy_doc)
    return iam.list_role_policies(RoleName=role_name)


def test_inline_role_policy_list(session: Session, inline_role_policy_list: t.ListRolePoliciesResponseTypeDef):
    assert inline_role_policy_list['PolicyNames'][0] == session.db.query(RolePolicy).first().PolicyName


def test_inline_role_policy_list_by_role(session: Session, inline_role_policy_list: t.ListRolePoliciesResponseTypeDef):
    live_name = inline_role_policy_list['PolicyNames'][0]
    role: Role = session.db.query(Role).first()
    assert live_name == role.inline_policies[0].PolicyName

# Listing updates the record but doesn't have a PolicyDocument associated with it, so make sure we don't delete the
# one that already exists with GetUserPolicy.
def test_inline_role_policy_get_then_list(session: Session, inline_role_policy: t.GetUserPolicyResponseTypeDef, inline_role_policy_list: t.ListUserPoliciesResponseTypeDef):
    #TODO: Return hash with UserPolicy.PolicyDocument
    assert inline_role_policy['PolicyDocument'] == json.loads(session.db.query(RolePolicy).first().PolicyDocument)


@pytest.fixture(scope='function')
def inline_role_policy(iam, role) -> t.GetRolePolicyResponseTypeDef:
    iam.put_role_policy(RoleName=role_name, PolicyName='test_policy', PolicyDocument=test_policy_doc)
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


