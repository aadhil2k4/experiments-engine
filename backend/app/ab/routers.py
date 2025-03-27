from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import authenticate_key, get_current_user
from ..database import get_async_session
from ..models import get_notifications_from_db, save_notifications_to_db
from ..schemas import EventType, NotificationsResponse, Outcome, RewardLikelihood
from ..users.models import UserDB
from .models import (
    delete_ab_experiment_by_id,
    get_ab_experiment_by_id,
    get_ab_observations_by_experiment_arm_id,
    get_ab_observations_by_experiment_id,
    get_all_ab_experiments,
    save_ab_observation_to_db,
    save_ab_to_db,
)
from .sampling_utils import choose_arm, update_arm_params
from .schemas import (
    ABExperiment,
    ABExperimentObservation,
    ABExperimentObservationResponse,
    ABExperimentResponse,
    ABExperimentSample,
    ArmResponse,
)

router = APIRouter(prefix="/ab", tags=["A/B Testing"])


@router.post("/", response_model=ABExperimentResponse)
async def create_ab_experiment(
    experiment: ABExperiment,
    user_db: Annotated[UserDB, Depends(get_current_user)],
    asession: AsyncSession = Depends(get_async_session),
) -> ABExperimentResponse:
    """
    Create a new experiment.
    """
    ab = await save_ab_to_db(experiment, user_db.user_id, asession)
    notifications = await save_notifications_to_db(
        experiment_id=ab.experiment_id,
        user_id=user_db.user_id,
        notifications=experiment.notifications,
        asession=asession,
    )

    ab_dict = ab.to_dict()
    ab_dict["notifications"] = [n.to_dict() for n in notifications]

    return ABExperimentResponse.model_validate(ab_dict)


@router.get("/", response_model=list[ABExperimentResponse])
async def get_abs(
    user_db: Annotated[UserDB, Depends(get_current_user)],
    asession: AsyncSession = Depends(get_async_session),
) -> list[ABExperimentResponse]:
    """
    Get details of all experiments.
    """
    experiments = await get_all_ab_experiments(user_db.user_id, asession)

    all_experiments = []
    for exp in experiments:
        exp_dict = exp.to_dict()
        exp_dict["notifications"] = [
            n.to_dict()
            for n in await get_notifications_from_db(
                exp.experiment_id, exp.user_id, asession
            )
        ]
        all_experiments.append(
            ABExperimentResponse.model_validate(
                {
                    **exp_dict,
                    "notifications": [
                        NotificationsResponse(**n) for n in exp_dict["notifications"]
                    ],
                }
            )
        )
    return all_experiments


@router.get("/{experiment_id}", response_model=ABExperimentResponse)
async def get_ab(
    experiment_id: int,
    user_db: Annotated[UserDB, Depends(get_current_user)],
    asession: AsyncSession = Depends(get_async_session),
) -> ABExperimentResponse:
    """
    Get details of experiment with the provided `experiment_id`.
    """
    experiment = await get_ab_experiment_by_id(experiment_id, user_db.user_id, asession)

    if experiment is None:
        raise HTTPException(
            status_code=404, detail=f"Experiment with id {experiment_id} not found"
        )

    experiment_dict = experiment.to_dict()
    experiment_dict["notifications"] = [
        n.to_dict()
        for n in await get_notifications_from_db(
            experiment.experiment_id, experiment.user_id, asession
        )
    ]

    return ABExperimentResponse.model_validate(experiment_dict)


@router.delete("/{experiment_id}", response_model=dict)
async def delete_ab(
    experiment_id: int,
    user_db: Annotated[UserDB, Depends(get_current_user)],
    asession: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    Delete the experiment with the provided `experiment_id`.
    """
    try:
        experiment = await get_ab_experiment_by_id(
            experiment_id, user_db.user_id, asession
        )
        if experiment is None:
            raise HTTPException(
                status_code=404, detail=f"Experiment with id {experiment_id} not found"
            )
        await delete_ab_experiment_by_id(experiment_id, user_db.user_id, asession)
        return {"message": f"Experiment with id {experiment_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}") from e


@router.get("/{experiment_id}/draw", response_model=ArmResponse)
async def draw_arm(
    experiment_id: int,
    user_db: UserDB = Depends(authenticate_key),
    asession: AsyncSession = Depends(get_async_session),
) -> ArmResponse:
    """
    Get which arm to pull next for provided experiment.
    """
    experiment = await get_ab_experiment_by_id(experiment_id, user_db.user_id, asession)

    if experiment is None:
        raise HTTPException(
            status_code=404, detail=f"Experiment with id {experiment_id} not found"
        )
    experiment_data = ABExperimentSample.model_validate(experiment)
    chosen_arm = choose_arm(experiment=experiment_data)
    return ArmResponse.model_validate(experiment.arms[chosen_arm])


@router.put("/{experiment_id}/{arm_id}/{outcome}", response_model=ArmResponse)
async def save_observation_for_arm(
    experiment_id: int,
    arm_id: int,
    outcome: float,
    user_db: UserDB = Depends(authenticate_key),
    asession: AsyncSession = Depends(get_async_session),
) -> ArmResponse:
    """
    Update the arm with the provided `arm_id` for the given
    `experiment_id` based on the `outcome`.
    """
    # Get and validate experiment
    experiment = await get_ab_experiment_by_id(experiment_id, user_db.user_id, asession)
    if experiment is None:
        raise HTTPException(
            status_code=404, detail=f"Experiment with id {experiment_id} not found"
        )
    experiment.n_trials += 1
    experiment_data = ABExperimentSample.model_validate(experiment)

    # Get and validate arm
    arms = [a for a in experiment.arms if a.arm_id == arm_id]
    if not arms:
        raise HTTPException(status_code=404, detail=f"Arm with id {arm_id} not found")

    arm = arms[0]

    if experiment_data.reward_type == RewardLikelihood.BERNOULLI:
        Outcome(outcome)  # Check if reward is 0 or 1

    observation = ABExperimentObservation(
        experiment_id=experiment.experiment_id,
        arm_id=arm.arm_id,
        reward=outcome,
    )
    await save_ab_observation_to_db(observation, user_db.user_id, asession)

    return ArmResponse.model_validate(arm)


@router.get(
    "/{experiment_id}/outcomes",
    response_model=list[ABExperimentObservationResponse],
)
async def get_outcomes(
    experiment_id: int,
    user_db: UserDB = Depends(authenticate_key),
    asession: AsyncSession = Depends(get_async_session),
) -> list[ABExperimentObservationResponse]:
    """
    Get the outcomes for the experiment.
    """
    experiment = await get_ab_experiment_by_id(experiment_id, user_db.user_id, asession)
    if not experiment:
        raise HTTPException(
            status_code=404, detail=f"Experiment with id {experiment_id} not found"
        )

    rewards = await get_ab_observations_by_experiment_id(
        experiment_id=experiment.experiment_id,
        user_id=user_db.user_id,
        asession=asession,
    )

    return [
        ABExperimentObservationResponse.model_validate(reward) for reward in rewards
    ]


@router.get(
    "/{experiment_id}/final",
    response_model=list[ArmResponse],
)
async def get_final_updated_arm(
    experiment_id: int,
    user_db: UserDB = Depends(authenticate_key),
    asession: AsyncSession = Depends(get_async_session),
) -> list[ArmResponse]:
    """
    Get the outcomes for the experiment.
    """
    # Check experiment params
    experiment = await get_ab_experiment_by_id(experiment_id, user_db.user_id, asession)
    if not experiment:
        raise HTTPException(
            status_code=404, detail=f"Experiment with id {experiment_id} not found"
        )

    # Return arms if update has already been done
    if experiment.done_final_update:
        return [ArmResponse.model_validate(arm) for arm in experiment.arms]

    # Check if the experiment has ended
    notification = await get_notifications_from_db(
        experiment_id=experiment.experiment_id,
        user_id=user_db.user_id,
        asession=asession,
    )
    if not notification:
        raise HTTPException(
            status_code=404,
            detail=f"No notifications for experiment {experiment_id} found.",
        )
    notification_data = NotificationsResponse.model_validate(notification[-1])

    if notification_data.notification_type == EventType.TRIALS_COMPLETED:
        if not (experiment.n_trials >= notification_data.notification_value):
            raise HTTPException(
                status_code=400,
                detail=f"Experiment {experiment_id} is not complete yet.",
            )
    elif notification_data.notification_type == EventType.DAYS_ELAPSED:
        now = datetime.now(timezone.utc)
        days_elapsed = (now - experiment.created_datetime_utc).days
        if not (days_elapsed >= notification_data.notification_value):
            raise HTTPException(
                status_code=400,
                detail=f"Experiment with id {experiment_id} is not complete yet.",
            )

    # Make final update
    experiment_data = ABExperimentSample.model_validate(experiment)

    arms_data = []
    for arm in experiment.arms:
        arm_rewards = await get_ab_observations_by_experiment_arm_id(
            experiment_id=experiment.experiment_id,
            arm_id=arm.arm_id,
            user_id=user_db.user_id,
            asession=asession,
        )
        rewards = [reward.reward for reward in arm_rewards]

        if experiment_data.reward_type == RewardLikelihood.BERNOULLI:
            arm.alpha, arm.beta = update_arm_params(
                ArmResponse.model_validate(arm),
                experiment_data.reward_type,
                rewards,
            )

        elif experiment_data.reward_type == RewardLikelihood.NORMAL:
            arm.mu, arm.sigma = update_arm_params(
                ArmResponse.model_validate(arm),
                experiment_data.reward_type,
                rewards,
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Reward type not supported.",
            )

        asession.add(arm)
        arms_data.append(ArmResponse.model_validate(arm))

    experiment.done_final_update = True
    asession.add(experiment)

    await asession.commit()

    return arms_data
