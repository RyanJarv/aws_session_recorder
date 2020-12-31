from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base  # type: ignore
from datetime import datetime, timezone
import sqlalchemy as sa

Base: DeclarativeMeta = declarative_base()


# Running on sqlite we'll hit timezone issues, utc not being used by the db.
# See https://mike.depalatis.net/blog/sqlalchemy-timestamps.html for more info.
class TimeStamp(sa.types.TypeDecorator):
    impl = sa.types.DateTime
    LOCAL_TIMEZONE = datetime.utcnow().astimezone().tzinfo

    def process_bind_param(self, value: datetime, dialect):
        if value.tzinfo is None:
            value = value.astimezone(self.LOCAL_TIMEZONE)

        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)
