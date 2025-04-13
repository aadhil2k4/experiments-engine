from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import authenticate_key, get_current_user
from ..database import get_async_session
from ..models import get_notifications_from_db, save_notifications_to_db
from ..schemas import NotificationsResponse, Outcome, RewardLikelihood
from ..users.models import UserDB
from .models import (
    delete_bayes_ab_experiment_by_id,
    get_all_bayes_ab_experiments,
    get_bayes_ab_experiment_by_id,
    get_bayes_ab_observations_by_experiment_id,
    save_bayes_ab_observation_to_db,
    save_bayes_ab_to_db,
)
from .sampling_utils import choose_arm, update_arm_params
from .schemas import (
    BayesABArmResponse,
    BayesianAB,
    BayesianABObservation,
    BayesianABObservationResponse,
    BayesianABResponse,
    BayesianABSample,
)

router = APIRouter(prefix="/bayes_ab", tags=["Bayesian A/B Testing"])


@router.post("/", response_model=BayesianABResponse)
async def create_ab_experiment(
    experiment: BayesianAB,
    user_db: Annotated[UserDB, Depends(get_current_user)],
    asession: AsyncSession = Depends(get_async_session),
) -> BayesianABResponse:
    """
    Create a new experiment.
    """
    bayes_ab = await save_bayes_ab_to_db(experiment, user_db.user_id, asession)
    notifications = await save_notifications_to_db(
        experiment_id=bayes_ab.experiment_id,
        user_id=user_db.user_id,
        notifications=experiment.notifications,
        asession=asession,
    )

    bayes_ab_dict = bayes_ab.to_dict()
    bayes_ab_dict["notifications"] = [n.to_dict() for n in notifications]

    return BayesianABResponse.model_validate(bayes_ab_dict)


@router.get("/", response_model=list[BayesianABResponse])
async def get_bayes_abs(
    user_db: Annotated[UserDB, Depends(get_current_user)],
    asession: AsyncSession = Depends(get_async_session),
) -> list[BayesianABResponse]:
    """
    Get details of all experiments.
    """
    experiments = await get_all_bayes_ab_experiments(user_db.user_id, asession)

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
            BayesianABResponse.model_validate(
                {
                    **exp_dict,
                    "notifications": [
                        NotificationsResponse(**n) for n in exp_dict["notifications"]
                    ],
                }
            )
        )
    return all_experiments


@router.get("/{experiment_id}", response_model=BayesianABResponse)
async def get_bayes_ab(
    experiment_id: int,
    user_db: Annotated[UserDB, Depends(get_current_user)],
    asession: AsyncSession = Depends(get_async_session),
) -> BayesianABResponse:
    """
    Get details of experiment with the provided `experiment_id`.
    """
    experiment = await get_bayes_ab_experiment_by_id(
        experiment_id, user_db.user_id, asession
    )

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

    return BayesianABResponse.model_validate(experiment_dict)


@router.delete("/{experiment_id}", response_model=dict)
async def delete_bayes_ab(
    experiment_id: int,
    user_db: Annotated[UserDB, Depends(get_current_user)],
    asession: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    Delete the experiment with the provided `experiment_id`.
    """
    try:
        experiment = await get_bayes_ab_experiment_by_id(
            experiment_id, user_db.user_id, asession
        )
        if experiment is None:
            raise HTTPException(
                status_code=404, detail=f"Experiment with id {experiment_id} not found"
            )
        await delete_bayes_ab_experiment_by_id(experiment_id, user_db.user_id, asession)
        return {"message": f"Experiment with id {experiment_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}") from e


@router.get("/{experiment_id}/draw", response_model=BayesABArmResponse)
async def draw_arm(
    experiment_id: int,
    user_db: UserDB = Depends(authenticate_key),
    asession: AsyncSession = Depends(get_async_session),
) -> BayesABArmResponse:
    """
    Get which arm to pull next for provided experiment.
    """
    experiment = await get_bayes_ab_experiment_by_id(
        experiment_id, user_db.user_id, asession
    )

    if experiment is None:
        raise HTTPException(
            status_code=404, detail=f"Experiment with id {experiment_id} not found"
        )
    experiment_data = BayesianABSample.model_validate(experiment)
    chosen_arm = choose_arm(experiment=experiment_data)
    return BayesABArmResponse.model_validate(experiment.arms[chosen_arm])


@router.put("/{experiment_id}/{arm_id}/{outcome}", response_model=BayesABArmResponse)
async def save_observation_for_arm(
    experiment_id: int,
    arm_id: int,
    outcome: float,
    user_db: UserDB = Depends(authenticate_key),
    asession: AsyncSession = Depends(get_async_session),
) -> BayesABArmResponse:
    """
    Update the arm with the provided `arm_id` for the given
    `experiment_id` based on the `outcome`.
    """
    # Get and validate experiment
    experiment = await get_bayes_ab_experiment_by_id(
        experiment_id, user_db.user_id, asession
    )
    if experiment is None:
        raise HTTPException(
            status_code=404, detail=f"Experiment with id {experiment_id} not found"
        )
    experiment.n_trials += 1
    experiment_data = BayesianABSample.model_validate(experiment)

    # Get and validate arm
    arms = [a for a in experiment.arms if a.arm_id == arm_id]
    if not arms:
        raise HTTPException(status_code=404, detail=f"Arm with id {arm_id} not found")

    arm = arms[0]
    arm.n_outcomes += 1

    if experiment_data.reward_type == RewardLikelihood.BERNOULLI:
        Outcome(outcome)  # Check if reward is 0 or 1

    observation = BayesianABObservation(
        experiment_id=experiment.experiment_id,
        arm_id=arm.arm_id,
        reward=outcome,
    )
    await save_bayes_ab_observation_to_db(observation, user_db.user_id, asession)

    return BayesABArmResponse.model_validate(arm)


@router.get(
    "/{experiment_id}/outcomes",
    response_model=list[BayesianABObservationResponse],
)
async def get_outcomes(
    experiment_id: int,
    user_db: UserDB = Depends(authenticate_key),
    asession: AsyncSession = Depends(get_async_session),
) -> list[BayesianABObservationResponse]:
    """
    Get the outcomes for the experiment.
    """
    experiment = await get_bayes_ab_experiment_by_id(
        experiment_id, user_db.user_id, asession
    )
    if not experiment:
        raise HTTPException(
            status_code=404, detail=f"Experiment with id {experiment_id} not found"
        )

    rewards = await get_bayes_ab_observations_by_experiment_id(
        experiment_id=experiment.experiment_id,
        user_id=user_db.user_id,
        asession=asession,
    )

    return [BayesianABObservationResponse.model_validate(reward) for reward in rewards]


@router.get(
    "/{experiment_id}/arms",
    response_model=list[BayesABArmResponse],
)
async def update_arms(
    experiment_id: int,
    user_db: UserDB = Depends(authenticate_key),
    asession: AsyncSession = Depends(get_async_session),
) -> list[BayesABArmResponse]:
    """
    Get the outcomes for the experiment.
    """
    # Check experiment params
    experiment = await get_bayes_ab_experiment_by_id(
        experiment_id, user_db.user_id, asession
    )
    if not experiment:
        raise HTTPException(
            status_code=404, detail=f"Experiment with id {experiment_id} not found"
        )

    # Make update
    experiment_data = BayesianABSample.model_validate(experiment)

    observations = await get_bayes_ab_observations_by_experiment_id(
        experiment_id=experiment.experiment_id,
        user_id=user_db.user_id,
        asession=asession,
    )

    if not observations:
        raise HTTPException(
            status_code=404,
            detail=f"No observations found for experiment {experiment_id}",
        )

    rewards = [obs.reward for obs in observations]

    arms_dict = {
        arm.arm_id: 1.0 if arm.is_treatment_arm else 0.0 for arm in experiment.arms
    }

    # Get params
    treatment_mu, treatment_sigma = [
        (arm.mu_init, arm.sigma_init) for arm in experiment.arms if arm.is_treatment_arm
    ][0]
    control_mu, control_sigma = [
        (arm.mu_init, arm.sigma_init)
        for arm in experiment.arms
        if not arm.is_treatment_arm
    ][0]
    treatments = [arms_dict[obs.arm_id] for obs in observations]

    new_means, new_sigmas = update_arm_params(
        experiment=experiment_data,
        mus=[treatment_mu, control_mu],
        sigmas=[treatment_sigma, control_sigma],
        rewards=rewards,
        treatments=treatments,
    )

    arms_data = []
    for arm in experiment.arms:
        if arm.is_treatment_arm:
            arm.mu = new_means[0]
            arm.sigma = new_sigmas[0]
        else:
            arm.mu = new_means[1]
            arm.sigma = new_sigmas[1]

        asession.add(arm)
        arms_data.append(BayesABArmResponse.model_validate(arm))

    asession.add(experiment)

    await asession.commit()

    return arms_data
