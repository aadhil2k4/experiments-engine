from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    and_,
    delete,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import (
    ArmBaseDB,
    ExperimentBaseDB,
    NotificationsDB,
    ObservationsBaseDB,
)
from .schemas import ABExperiment, ABExperimentObservation


class ABExperimentDB(ExperimentBaseDB):
    """
    ORM for managing experiments.
    """

    __tablename__ = "ab_experiments"

    experiment_id: Mapped[int] = mapped_column(
        ForeignKey("experiments_base.experiment_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    arms: Mapped[list["ABArmDB"]] = relationship(
        "ABArmDB", back_populates="experiment", lazy="joined"
    )

    observations: Mapped[list["ABObservationDB"]] = relationship(
        "ABObservationDB", back_populates="experiment", lazy="joined"
    )

    done_final_update: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "ab_experiments"}

    def to_dict(self) -> dict:
        """
        Convert the ORM object to a dictionary.
        """
        return {
            "experiment_id": self.experiment_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "created_datetime_utc": self.created_datetime_utc,
            "is_active": self.is_active,
            "n_trials": self.n_trials,
            "arms": [arm.to_dict() for arm in self.arms],
            "prior_type": self.prior_type,
            "reward_type": self.reward_type,
            "done_final_update": self.done_final_update,
        }


class ABArmDB(ArmBaseDB):
    """
    ORM for managing arms.
    """

    __tablename__ = "ab_arms"

    arm_id: Mapped[int] = mapped_column(
        ForeignKey("arms_base.arm_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    # prior variables for AB arms
    alpha: Mapped[float] = mapped_column(Float, nullable=True)
    beta: Mapped[float] = mapped_column(Float, nullable=True)
    mu: Mapped[float] = mapped_column(Float, nullable=True)
    sigma: Mapped[float] = mapped_column(Float, nullable=True)

    experiment: Mapped[ABExperimentDB] = relationship(
        "ABExperimentDB", back_populates="arms", lazy="joined"
    )
    observations: Mapped[list["ABObservationDB"]] = relationship(
        "ABObservationDB", back_populates="arm", lazy="joined"
    )

    __mapper_args__ = {"polymorphic_identity": "ab_arms"}

    def to_dict(self) -> dict:
        """
        Convert the ORM object to a dictionary.
        """
        return {
            "arm_id": self.arm_id,
            "name": self.name,
            "description": self.description,
            "alpha": self.alpha,
            "beta": self.beta,
            "mu": self.mu,
            "sigma": self.sigma,
            "observations": [obs.to_dict() for obs in self.observations],
        }


class ABObservationDB(ObservationsBaseDB):
    """
    ORM for managing observations of AB experiment.
    """

    __tablename__ = "ab_observations"

    observation_id: Mapped[int] = mapped_column(
        ForeignKey("observations_base.observation_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    reward: Mapped[float] = mapped_column(Float, nullable=False)

    arm: Mapped[ABArmDB] = relationship(
        "ABArmDB", back_populates="observations", lazy="joined"
    )
    experiment: Mapped[ABExperimentDB] = relationship(
        "ABExperimentDB", back_populates="observations", lazy="joined"
    )

    __mapper_args__ = {"polymorphic_identity": "ab_observations"}

    def to_dict(self) -> dict:
        """
        Convert the ORM object to a dictionary.
        """
        return {
            "observation_id": self.observation_id,
            "reward": self.reward,
            "created_datetime_utc": self.observed_datetime_utc,
        }


async def save_ab_to_db(
    ab_experiment: ABExperiment,
    user_id: int,
    asession: AsyncSession,
) -> ABExperimentDB:
    """
    Save the A/B experiment to the database.
    """
    arms = [ABArmDB(**arm.model_dump(), user_id=user_id) for arm in ab_experiment.arms]

    ab_experiment_db = ABExperimentDB(
        user_id=user_id,
        name=ab_experiment.name,
        description=ab_experiment.description,
        created_datetime_utc=datetime.now(timezone.utc),
        is_active=ab_experiment.is_active,
        done_final_update=False,
        n_trials=0,
        arms=arms,
        prior_type=ab_experiment.prior_type,
        reward_type=ab_experiment.reward_type,
    )

    asession.add(ab_experiment_db)
    await asession.commit()
    await asession.refresh(ab_experiment_db)

    return ab_experiment_db


async def get_all_ab_experiments(
    user_id: int,
    asession: AsyncSession,
) -> Sequence[ABExperimentDB]:
    """
    Get all the A/B experiments from the database.
    """
    stmt = (
        select(ABExperimentDB)
        .where(ABExperimentDB.user_id == user_id)
        .order_by(ABExperimentDB.experiment_id)
    )
    result = await asession.execute(stmt)
    return result.unique().scalars().all()


async def get_ab_experiment_by_id(
    experiment_id: int,
    user_id: int,
    asession: AsyncSession,
) -> ABExperimentDB | None:
    """
    Get the A/B experiment by id.
    """
    stmt = select(ABExperimentDB).where(
        and_(
            ABExperimentDB.user_id == user_id,
            ABExperimentDB.experiment_id == experiment_id,
        )
    )
    result = await asession.execute(stmt)
    return result.unique().scalar_one_or_none()


async def delete_ab_experiment_by_id(
    experiment_id: int,
    user_id: int,
    asession: AsyncSession,
) -> None:
    """
    Delete the A/B experiment by id.
    """
    stmt = delete(ABExperimentDB).where(
        and_(
            ABExperimentDB.user_id == user_id,
            ABExperimentDB.experiment_id == experiment_id,
        )
    )
    await asession.execute(stmt)

    stmt = delete(NotificationsDB).where(
        and_(
            NotificationsDB.user_id == user_id,
            NotificationsDB.experiment_id == experiment_id,
        )
    )
    await asession.execute(stmt)

    stmt = delete(ABObservationDB).where(
        and_(
            ABObservationDB.user_id == user_id,
            ABObservationDB.experiment_id == experiment_id,
        )
    )
    await asession.execute(stmt)

    stmt = delete(ABArmDB).where(
        and_(
            ABArmDB.user_id == user_id,
            ABArmDB.experiment_id == experiment_id,
        )
    )
    await asession.execute(stmt)

    await asession.commit()
    return None


async def save_ab_observation_to_db(
    ab_observation: ABExperimentObservation,
    user_id: int,
    asession: AsyncSession,
) -> ABObservationDB:
    """
    Save the A/B observation to the database.
    """
    ab_observation_db = ABObservationDB(
        **ab_observation.model_dump(),
        user_id=user_id,
        observed_datetime_utc=datetime.now(timezone.utc),
    )

    asession.add(ab_observation_db)
    await asession.commit()
    await asession.refresh(ab_observation_db)

    return ab_observation_db


async def get_ab_observations_by_experiment_arm_id(
    experiment_id: int,
    arm_id: int,
    user_id: int,
    asession: AsyncSession,
) -> Sequence[ABObservationDB]:
    """
    Get the observations of the A/B experiment by id.
    """
    stmt = (
        select(ABObservationDB)
        .where(
            and_(
                ABObservationDB.user_id == user_id,
                ABObservationDB.experiment_id == experiment_id,
                ABObservationDB.arm_id == arm_id,
            )
        )
        .order_by(ABObservationDB.observed_datetime_utc)
    )

    result = await asession.execute(stmt)
    return result.unique().scalars().all()


async def get_ab_observations_by_experiment_id(
    experiment_id: int,
    user_id: int,
    asession: AsyncSession,
) -> Sequence[ABObservationDB]:
    """
    Get the observations of the A/B experiment by id.
    """
    stmt = (
        select(ABObservationDB)
        .where(
            and_(
                ABObservationDB.user_id == user_id,
                ABObservationDB.experiment_id == experiment_id,
            )
        )
        .order_by(ABObservationDB.observed_datetime_utc)
    )

    result = await asession.execute(stmt)
    return result.unique().scalars().all()
