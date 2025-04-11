from datetime import datetime
from typing import Optional, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..mab.schemas import (
    MABObservation,
    MABObservationResponse,
    MultiArmedBanditBase,
)
from ..schemas import Notifications, NotificationsResponse, allowed_combos_bayes_ab


class BayesABArm(BaseModel):
    """
    Pydantic model for a arm of the experiment.
    """

    name: str = Field(
        max_length=150,
        examples=["Arm 1"],
    )
    description: str = Field(
        max_length=500,
        examples=["This is a description of the arm."],
    )

    mu: float = Field(
        default=0.0, description="Mean parameter for treatment effect prior"
    )
    sigma: float = Field(
        default=1.0, description="Std dev parameter for treatment effect prior"
    )
    n_outcomes: Optional[int] = Field(
        default=0,
        description="Number of outcomes for the arm",
        examples=[0, 10, 15],
    )

    @model_validator(mode="after")
    def check_values(self) -> Self:
        """
        Check if the values are unique and set new attributes.
        """
        if self.sigma is not None and self.sigma <= 0:
            raise ValueError("Std dev must be greater than 0.")
        return self

    model_config = ConfigDict(from_attributes=True)


class BayesABArmResponse(BayesABArm):
    """
    Pydantic model for a response for contextual arm creation
    """

    arm_id: int
    model_config = ConfigDict(from_attributes=True)


class BayesianAB(MultiArmedBanditBase):
    """
    Pydantic model for an A/B experiment.
    """

    arms: list[BayesABArm]
    notifications: Notifications
    done_final_update: bool = False
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def arms_exactly_two(self) -> Self:
        """
        Validate that the experiment has exactly two arms.
        """
        if len(self.arms) != 2:
            raise ValueError("The experiment must have at exactly two arms.")
        return self

    @model_validator(mode="after")
    def check_prior_reward_type_combo(self) -> Self:
        """
        Validate that the prior and reward type combination is allowed.
        """

        if (self.prior_type, self.reward_type) not in allowed_combos_bayes_ab:
            raise ValueError("Prior and reward type combo not supported.")
        return self


class BayesianABResponse(MultiArmedBanditBase):
    """
    Pydantic model for a response for an A/B experiment.
    """

    experiment_id: int
    done_final_update: bool
    arms: list[BayesABArmResponse]
    notifications: list[NotificationsResponse]
    created_datetime_utc: datetime
    last_trial_datetime_utc: Optional[datetime] = None
    n_trials: int

    model_config = ConfigDict(from_attributes=True)


class BayesianABSample(MultiArmedBanditBase):
    """
    Pydantic model for a sample A/B experiment.
    """

    experiment_id: int
    arms: list[BayesABArmResponse]
    done_final_update: bool


class BayesianABObservation(MABObservation):
    """
    Pydantic model for an observation in an A/B experiment.
    """

    pass


class BayesianABObservationResponse(MABObservationResponse):
    """
    Pydantic model for an observation response in an A/B experiment.
    """

    pass
