from datetime import datetime
from typing import Self

from pydantic import ConfigDict, model_validator

from ..mab.schemas import (
    Arm,
    ArmResponse,
    MABObservation,
    MABObservationResponse,
    MultiArmedBanditBase,
)
from ..schemas import (
    ArmPriors,
    Notifications,
    NotificationsResponse,
    allowed_combos_mab,
)


class ABExperiment(MultiArmedBanditBase):
    """
    Pydantic model for an A/B experiment.
    """

    arms: list[Arm]
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

        if (self.prior_type, self.reward_type) not in allowed_combos_mab:
            raise ValueError("Prior and reward type combo not supported.")
        return self

    @model_validator(mode="after")
    def check_arm_missing_params(self) -> Self:
        """
        Check if the arm reward type is same as the experiment reward type.
        """
        prior_type = self.prior_type
        arms = self.arms

        prior_params = {
            ArmPriors.BETA: ("alpha", "beta"),
            ArmPriors.NORMAL: ("mu", "sigma"),
        }

        for arm in arms:
            arm_dict = arm.model_dump()
            if prior_type in prior_params:
                missing_params = []
                for param in prior_params[prior_type]:
                    if param not in arm_dict.keys():
                        missing_params.append(param)
                    elif arm_dict[param] is None:
                        missing_params.append(param)

                if missing_params:
                    val = prior_type.value
                    raise ValueError(f"{val} prior needs {','.join(missing_params)}.")
        return self

    @model_validator(mode="after")
    def check_notification_params(self) -> Self:
        """
        Check if the notification parameters are valid.
        """

        if (not self.notifications.onTrialCompletion) and (
            not self.notifications.onDaysElapsed
        ):
            raise ValueError(
                "At least one of trials completed\
                              or days elapsed must be enabled."
            )

        if self.notifications.onPercentBetter:
            raise ValueError("Percent better is not supported for A/B tests.")

        return self

    model_config = ConfigDict(from_attributes=True)


class ABExperimentResponse(MultiArmedBanditBase):
    """
    Pydantic model for a response for an A/B experiment.
    """

    experiment_id: int
    done_final_update: bool
    arms: list[ArmResponse]
    notifications: list[NotificationsResponse]
    created_datetime_utc: datetime
    n_trials: int

    model_config = ConfigDict(from_attributes=True)


class ABExperimentSample(MultiArmedBanditBase):
    """
    Pydantic model for a sample A/B experiment.
    """

    experiment_id: int
    arms: list[ArmResponse]
    done_final_update: bool


class ABExperimentObservation(MABObservation):
    """
    Pydantic model for an observation in an A/B experiment.
    """

    pass


class ABExperimentObservationResponse(MABObservationResponse):
    """
    Pydantic model for an observation response in an A/B experiment.
    """

    pass
