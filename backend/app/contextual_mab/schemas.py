from datetime import datetime
from typing import Optional, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..schemas import (
    ArmPriors,
    ContextType,
    Notifications,
    NotificationsResponse,
    RewardLikelihood,
    allowed_combos_cmab,
)


class Context(BaseModel):
    """
    Pydantic model for a binary-valued context of the experiment.
    """

    name: str = Field(
        description="Name of the context",
        examples=["Context 1"],
    )
    description: str = Field(
        description="Description of the context",
        examples=["This is a description of the context."],
    )
    value_type: ContextType = Field(
        description="Type of value the context can take", default=ContextType.BINARY
    )
    model_config = ConfigDict(from_attributes=True)


class ContextResponse(Context):
    """
    Pydantic model for an response for context creation
    """

    context_id: int
    model_config = ConfigDict(from_attributes=True)


class ContextInput(BaseModel):
    """
    Pydantic model for a context input
    """

    context_id: int
    context_value: float
    model_config = ConfigDict(from_attributes=True)


class ContextualArm(BaseModel):
    """
    Pydantic model for a contextual arm of the experiment.
    """

    name: str = Field(
        max_length=150,
        examples=["Arm 1"],
    )
    description: str = Field(
        max_length=500,
        examples=["This is a description of the arm."],
    )

    mu_init: float = Field(
        default=0.0,
        examples=[0.0, 1.2, 5.7],
        description="Mean parameter for Normal prior",
    )

    sigma_init: float = Field(
        default=1.0,
        examples=[1.0, 0.5, 2.0],
        description="Standard deviation parameter for Normal prior",
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
        sigma = self.sigma_init
        if sigma is not None and sigma <= 0:
            raise ValueError("Std dev must be greater than 0.")
        return self

    model_config = ConfigDict(from_attributes=True)


class ContextualArmResponse(ContextualArm):
    """
    Pydantic model for an response for contextual arm creation
    """

    arm_id: int
    mu: list[float]
    covariance: list[list[float]]

    model_config = ConfigDict(from_attributes=True)


class ContextualBanditBase(BaseModel):
    """
    Pydantic model for a contextual experiment - Base model.
    Note: Do not use this model directly. Use ContextualBandit instead.
    """

    name: str = Field(
        max_length=150,
        examples=["Experiment 1"],
    )

    description: str = Field(
        max_length=500,
        examples=["This is a description of the experiment."],
    )

    reward_type: RewardLikelihood = Field(
        description="The type of reward we observe from the experiment.",
        default=RewardLikelihood.BERNOULLI,
    )

    prior_type: ArmPriors = Field(
        description="The type of prior distribution for the arms.",
        default=ArmPriors.NORMAL,
    )

    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class ContextualBandit(ContextualBanditBase):
    """
    Pydantic model for a contextual experiment.
    """

    arms: list[ContextualArm]
    contexts: list[Context]
    notifications: Notifications

    @model_validator(mode="after")
    def arms_at_least_two(self) -> Self:
        """
        Validate that the experiment has at least two arms.
        """
        if len(self.arms) < 2:
            raise ValueError("The experiment must have at least two arms.")
        return self

    @model_validator(mode="after")
    def check_prior_reward_type_combo(self) -> Self:
        """
        Validate that the prior and reward type combination is allowed.
        """

        if (self.prior_type, self.reward_type) not in allowed_combos_cmab:
            raise ValueError("Prior and reward type combo not supported.")
        return self

    model_config = ConfigDict(from_attributes=True)


class ContextualBanditResponse(ContextualBanditBase):
    """
    Pydantic model for an response for contextual experiment creation.
    Returns the id of the experiment, the arms and the contexts
    """

    experiment_id: int
    arms: list[ContextualArmResponse]
    contexts: list[ContextResponse]
    notifications: list[NotificationsResponse]
    created_datetime_utc: datetime
    last_trial_datetime_utc: Optional[datetime] = None
    n_trials: int

    model_config = ConfigDict(from_attributes=True)


class ContextualBanditSample(ContextualBanditBase):
    """
    Pydantic model for a contextual experiment sample.
    """

    experiment_id: int
    arms: list[ContextualArmResponse]
    contexts: list[ContextResponse]


class CMABObservation(BaseModel):
    """
    Pydantic model for a contextual observation of the experiment.
    """

    arm_id: int
    reward: float
    context_val: list[float]

    model_config = ConfigDict(from_attributes=True)


class CMABObservationResponse(CMABObservation):
    """
    Pydantic model for an response for contextual observation creation
    """

    observation_id: int
    observed_datetime_utc: datetime

    model_config = ConfigDict(from_attributes=True)
