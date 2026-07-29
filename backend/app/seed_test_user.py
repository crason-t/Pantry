"""Seed fixture for the local test account used during manual dev/testing.

test@mail.com is NOT a real user -- it's the fixed account developers log into
when poking around locally. Run with: `uv run python -m app.seed_test_user`.
Idempotent: if the account already exists, this does nothing (so it never
clobbers whatever password/state a given dev environment already has for it).
Safe to run against any environment, including a fresh DB in a new worktree.
"""

from app.auth.security import hash_password
from app.db import SessionLocal
from app.models.user import User

TEST_USER_EMAIL = "test@mail.com"
TEST_USER_USERNAME = "a"
TEST_USER_PASSWORD = "password"  # local dev fixture only -- never used in a real environment


def seed_test_user() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == TEST_USER_EMAIL).first()
        if existing is not None:
            print(f"Test user already exists (id={existing.id}, username={existing.username}) -- skipping")
            return
        user = User(
            email=TEST_USER_EMAIL,
            username=TEST_USER_USERNAME,
            hashed_password=hash_password(TEST_USER_PASSWORD),
        )
        db.add(user)
        db.commit()
        print(f"Created test user: {TEST_USER_EMAIL} / {TEST_USER_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_test_user()
