import json
from sqlalchemy import JSON, Column, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.core.domain import ScheduleRepository, Schedule
from src.common import get_platform_path
from ..domain.exceptions import AppCodeError

Base_schedule = declarative_base()


class ScheduleModel(Base_schedule):
    __tablename__ = "schedules"

    id = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    date = Column(String, nullable=False)
    items = Column(JSON, nullable=False)

    @staticmethod
    def from_entity(schedule: Schedule) -> "ScheduleModel":
        return ScheduleModel(
            id=schedule.id,
            name=schedule.name,
            date=schedule.date,
            items=json.dumps(schedule.items),
        )

    def to_entity(self) -> Schedule:
        return Schedule(
            id=self.id, name=self.name, date=self.date, items=json.loads(self.items)
        )

    def update_from_entity(self, schedule: Schedule):
        self.name = schedule.name
        self.date = schedule.date
        self.items = json.dumps(schedule.items)


class SQLiteScheduleRepository(ScheduleRepository):
    def __init__(self):
        self.db_path = get_platform_path("appdata", "databases", "schedules.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(f"sqlite:///{self.db_path}")
        Base_schedule.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def add(self, schedule):
        with self.Session() as session:
            existing_by_name = (
                session.query(ScheduleModel)
                .filter(ScheduleModel.name == schedule.name)
                .first()
            )

            if existing_by_name:
                raise AppCodeError("schedule.duplicated")

            schedule_model = ScheduleModel.from_entity(schedule)
            session.add(schedule_model)
            session.commit()

    def update(self, schedule):
        with self.Session() as session:
            schedule_model = (
                session.query(ScheduleModel)
                .filter(ScheduleModel.id == schedule.id)
                .first()
            )
            if schedule_model:
                schedule_model.update_from_entity(schedule)
                session.commit()
                return
        raise AppCodeError("song.not_found")

    def get(self, reference):
        with self.Session() as session:
            query = session.query(ScheduleModel)
            for key, value in reference.items():
                query = query.filter(getattr(ScheduleModel, key) == value)
            schedule_model = query.first()
            if schedule_model:
                return schedule_model.to_entity()
        raise AppCodeError("song.not_found")

    def get_all(self, reference=None) -> list[Schedule]:
        with self.Session() as session:
            query = session.query(ScheduleModel)
            if reference:
                for key, value in reference.items():
                    query = query.filter(getattr(ScheduleModel, key) == value)
            schedules_model = query.all()
            return [model.to_entity() for model in schedules_model]

    def delete(self, reference):
        with self.Session() as session:
            query = session.query(ScheduleModel)
            for key, value in reference.items():
                query = query.filter(getattr(ScheduleModel, key) == value)
            schedule_model = query.first()
            if schedule_model:
                session.delete(schedule_model)
                session.commit()
                return
        raise AppCodeError("song.not_found")
