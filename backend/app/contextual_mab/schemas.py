import numpy as np
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
from ..mab.schemas import MultiArmedBandit, MultiArmedBanditResponse


class ContextType(Enum):
    """
    Enum class for the type of context.
    """

    BINARY = "binary"
    CATEGORICAL = "categorical"
    CONTINUOUS = "continuous"


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
    context_type: str = Field(
        examples=["binary", "categorical", "continuous"],
        description="Type of context",
    )
    values: List[int] = Field(
        description="List of values the context can", examples=[[0, 1]]
    )
    weight: float = Field(
        description="Weight associated with outcome for this context",
        examples=[1.0, 3.7, 0.5],
        default=1.0,
    )

    model_config = ConfigDict(from_attributes=True)


class ContextResponse(Context):
    """
    Pydantic model for an response for context creation
    """

    context_id: int
    model_config = ConfigDict(from_attributes=True)


class ContextualArmInput(BaseModel):
    """
    Pydantic model for input to update an arm.
    """

    name: str = Field(
        max_length=150,
        examples=["Arm 1"],
    )
    description: str = Field(
        max_length=500,
        examples=["This is a description of the arm."],
    )

    alpha_prior: int = Field(
        description="The alpha parameter of the beta distribution.",
        examples=[1, 10, 100],
    )
    beta_prior: int = Field(
        description="The beta parameter of the beta distribution.",
        examples=[1, 10, 100],
    )

    model_config = ConfigDict(from_attributes=True)


class ContextualArm(ContextualArmInput):
    """
    Pydantic model for a contextual arm of the experiment.
    """

    successes: list = Field(
        description="List of successes corresponding to each context combo.",
        examples=[np.zeros((2, 3)).tolist()],
    )
    failures: Optional[list] = Field(
        description="List of failures corresponding to each context combo.",
        examples=[np.zeros((2, 3)).tolist()],
    )
    model_config = ConfigDict(from_attributes=True)


class ContextualArmResponse(ContextualArm):
    """
    Pydantic model for an response for contextual arm creation
    """

    arm_id: int
    model_config = ConfigDict(from_attributes=True)


class ContextualBanditInput(MultiArmedBandit):
    """
    Pydantic model for a contextual experiment.
    """

    arms: list[ContextualArmInput]
    contexts: list[Context]

    model_config = ConfigDict(from_attributes=True)


class ContextualBandit(MultiArmedBandit):
    """
    Pydantic model for a contextual experiment.
    """

    arms: list[ContextualArm]
    contexts: list[Context]

    model_config = ConfigDict(from_attributes=True)


class ContextualBanditResponse(MultiArmedBanditResponse):
    """
    Pydantic model for an response for contextual experiment creation.
    Returns the id of the experiment, the arms and the contexts
    """

    arms: list[ContextualArmResponse]
    contexts: list[ContextResponse]

    model_config = ConfigDict(from_attributes=True)
