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
from .schemas import BayesianAB, BayesianABObservation


class BayesianABDB(ExperimentBaseDB):
    """
    ORM for managing experiments.
    """

    __tablename__ = "bayes_ab_experiments"

    experiment_id: Mapped[int] = mapped_column(
        ForeignKey("experiments_base.experiment_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    arms: Mapped[list["BayesianABArmDB"]] = relationship(
        "BayesianABArmDB", back_populates="experiment", lazy="joined"
    )

    observations: Mapped[list["BayesianABObservationDB"]] = relationship(
        "BayesianABObservationDB", back_populates="experiment", lazy="joined"
    )

    __mapper_args__ = {"polymorphic_identity": "bayes_ab_experiments"}

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
        }


class BayesianABArmDB(ArmBaseDB):
    """
    ORM for managing arms.
    """

    __tablename__ = "bayes_ab_arms"

    arm_id: Mapped[int] = mapped_column(
        ForeignKey("arms_base.arm_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    # prior variables for AB arms
    mu_init: Mapped[float] = mapped_column(Float, nullable=False)
    sigma_init: Mapped[float] = mapped_column(Float, nullable=False)
    mu: Mapped[float] = mapped_column(Float, nullable=False)
    sigma: Mapped[float] = mapped_column(Float, nullable=False)
    is_treatment_arm: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    experiment: Mapped[BayesianABDB] = relationship(
        "BayesianABDB", back_populates="arms", lazy="joined"
    )
    observations: Mapped[list["BayesianABObservationDB"]] = relationship(
        "BayesianABObservationDB", back_populates="arm", lazy="joined"
    )

    __mapper_args__ = {"polymorphic_identity": "bayes_ab_arms"}

    def to_dict(self) -> dict:
        """
        Convert the ORM object to a dictionary.
        """
        return {
            "arm_id": self.arm_id,
            "name": self.name,
            "description": self.description,
            "mu_init": self.mu_init,
            "sigma_init": self.sigma_init,
            "mu": self.mu,
            "sigma": self.sigma,
            "is_treatment_arm": self.is_treatment_arm,
            "observations": [obs.to_dict() for obs in self.observations],
        }


class BayesianABObservationDB(ObservationsBaseDB):
    """
    ORM for managing observations of AB experiment.
    """

    __tablename__ = "bayes_ab_observations"

    observation_id: Mapped[int] = mapped_column(
        ForeignKey("observations_base.observation_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    reward: Mapped[float] = mapped_column(Float, nullable=False)

    arm: Mapped[BayesianABArmDB] = relationship(
        "BayesianABArmDB", back_populates="observations", lazy="joined"
    )
    experiment: Mapped[BayesianABDB] = relationship(
        "BayesianABDB", back_populates="observations", lazy="joined"
    )

    __mapper_args__ = {"polymorphic_identity": "bayes_ab_observations"}

    def to_dict(self) -> dict:
        """
        Convert the ORM object to a dictionary.
        """
        return {
            "observation_id": self.observation_id,
            "reward": self.reward,
            "observed_datetime_utc": self.observed_datetime_utc,
        }


async def save_bayes_ab_to_db(
    ab_experiment: BayesianAB,
    user_id: int,
    asession: AsyncSession,
) -> BayesianABDB:
    """
    Save the A/B experiment to the database.
    """
    arms = [
        BayesianABArmDB(
            **arm.model_dump(), mu=arm.mu_init, sigma=arm.sigma_init, user_id=user_id
        )
        for arm in ab_experiment.arms
    ]

    bayes_ab_db = BayesianABDB(
        user_id=user_id,
        name=ab_experiment.name,
        description=ab_experiment.description,
        created_datetime_utc=datetime.now(timezone.utc),
        is_active=ab_experiment.is_active,
        n_trials=0,
        arms=arms,
        prior_type=ab_experiment.prior_type,
        reward_type=ab_experiment.reward_type,
    )

    asession.add(bayes_ab_db)
    await asession.commit()
    await asession.refresh(bayes_ab_db)

    return bayes_ab_db


async def get_all_bayes_ab_experiments(
    user_id: int,
    asession: AsyncSession,
) -> Sequence[BayesianABDB]:
    """
    Get all the A/B experiments from the database.
    """
    stmt = (
        select(BayesianABDB)
        .where(BayesianABDB.user_id == user_id)
        .order_by(BayesianABDB.experiment_id)
    )
    result = await asession.execute(stmt)
    return result.unique().scalars().all()


async def get_bayes_ab_experiment_by_id(
    experiment_id: int,
    user_id: int,
    asession: AsyncSession,
) -> BayesianABDB | None:
    """
    Get the A/B experiment by id.
    """
    stmt = select(BayesianABDB).where(
        and_(
            BayesianABDB.user_id == user_id,
            BayesianABDB.experiment_id == experiment_id,
        )
    )
    result = await asession.execute(stmt)
    return result.unique().scalar_one_or_none()


async def delete_bayes_ab_experiment_by_id(
    experiment_id: int,
    user_id: int,
    asession: AsyncSession,
) -> None:
    """
    Delete the A/B experiment by id.
    """
    stmt = delete(BayesianABDB).where(
        and_(
            BayesianABDB.user_id == user_id,
            BayesianABDB.experiment_id == experiment_id,
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

    stmt = delete(BayesianABObservationDB).where(
        and_(
            BayesianABObservationDB.user_id == user_id,
            BayesianABObservationDB.experiment_id == experiment_id,
        )
    )
    await asession.execute(stmt)

    stmt = delete(BayesianABArmDB).where(
        and_(
            BayesianABArmDB.user_id == user_id,
            BayesianABArmDB.experiment_id == experiment_id,
        )
    )
    await asession.execute(stmt)

    await asession.commit()
    return None


async def save_bayes_ab_observation_to_db(
    ab_observation: BayesianABObservation,
    user_id: int,
    asession: AsyncSession,
) -> BayesianABObservationDB:
    """
    Save the A/B observation to the database.
    """
    ab_observation_db = BayesianABObservationDB(
        **ab_observation.model_dump(),
        user_id=user_id,
        observed_datetime_utc=datetime.now(timezone.utc),
    )

    asession.add(ab_observation_db)
    await asession.commit()
    await asession.refresh(ab_observation_db)

    return ab_observation_db


async def get_bayes_ab_observations_by_experiment_arm_id(
    experiment_id: int,
    arm_id: int,
    user_id: int,
    asession: AsyncSession,
) -> Sequence[BayesianABObservationDB]:
    """
    Get the observations of the A/B experiment by id.
    """
    stmt = (
        select(BayesianABObservationDB)
        .where(
            and_(
                BayesianABObservationDB.user_id == user_id,
                BayesianABObservationDB.experiment_id == experiment_id,
                BayesianABObservationDB.arm_id == arm_id,
            )
        )
        .order_by(BayesianABObservationDB.observed_datetime_utc)
    )

    result = await asession.execute(stmt)
    return result.unique().scalars().all()


async def get_bayes_ab_observations_by_experiment_id(
    experiment_id: int,
    user_id: int,
    asession: AsyncSession,
) -> Sequence[BayesianABObservationDB]:
    """
    Get the observations of the A/B experiment by id.
    """
    stmt = (
        select(BayesianABObservationDB)
        .where(
            and_(
                BayesianABObservationDB.user_id == user_id,
                BayesianABObservationDB.experiment_id == experiment_id,
            )
        )
        .order_by(BayesianABObservationDB.observed_datetime_utc)
    )

    result = await asession.execute(stmt)
    return result.unique().scalars().all()
