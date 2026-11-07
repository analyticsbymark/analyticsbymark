from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select


class Policy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_of_business: str
    broker: str
    premium_oc: int
    currency: Optional[str] = 'USD'
    is_cat_exposed: Optional[bool] = False


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_policies():
    policy_1 = Policy(class_of_business='Property', broker='London Brokers', premium_oc=50000, is_cat_exposed=True)
    policy_2 = Policy(class_of_business='Marine', broker='Singapore Brokers', premium_oc=25000)
    policy_3 = Policy(class_of_business='Property', broker='Australia Brokers', premium_oc=10000, currency='AUD')

    with Session(engine) as session:
        session.add(policy_1)
        session.add(policy_2)
        session.add(policy_3)

        session.commit()


def select_policies():
    with Session(engine) as session:
        statement = select(Policy)
        results = session.exec(statement)
        for policy in results:
            print(policy)


def main():
    create_db_and_tables()
    create_policies()
    select_policies()


if __name__ == "__main__":
    main()