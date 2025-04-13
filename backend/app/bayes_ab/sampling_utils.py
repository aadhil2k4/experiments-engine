import numpy as np
from scipy.optimize import minimize

from ..schemas import ArmPriors, ContextLinkFunctions, RewardLikelihood
from .schemas import BayesianABSample


def _update_arms(
    mus: np.ndarray,
    sigmas: np.ndarray,
    rewards: np.ndarray,
    treatments: np.ndarray,
    link_function: ContextLinkFunctions,
    reward_likelihood: RewardLikelihood,
    prior_type: ArmPriors,
) -> tuple[list, list]:
    """
    Get arm posteriors.

    Parameters
    ----------
    mu : np.ndarray
        The mean of the Normal distribution.
    sigma : np.ndarray
        The standard deviation of the Normal distribution.
    rewards : np.ndarray
        The rewards.
    treatments : np.ndarray
        The treatments (binary-valued).
    link_function : ContextLinkFunctions
        The link function for parameters to rewards.
    reward_likelihood : RewardLikelihood
        The likelihood function of the reward.
    prior_type : ArmPriors
        The prior type of the arm.
    """

    # TODO we explicitly assume that there is only 1 treatment arm
    def objective(treatment_effect_arms_bias: np.ndarray) -> float:
        """
        Objective function for arm to outcome.

        Parameters
        ----------
        treatment_effect : float
            The treatment effect.
        """
        treatment, control, bias = treatment_effect_arms_bias

        # log prior
        log_prior = prior_type(
            np.array([treatment, control]), mu=mus, covariance=np.diag(sigmas)
        )

        # log likelihood
        log_likelihood = reward_likelihood(
            rewards,
            link_function(treatment * treatments + control * (1 - treatments) + bias),
        )
        return -(log_prior + log_likelihood)

    result = minimize(objective, x0=np.zeros(3), method="L-BFGS-B", hess="2-point")
    new_treatment_mean, new_control_mean, _ = result.x
    new_treatment_sigma, new_control_sigma, _ = np.sqrt(
        np.diag(result.hess_inv.todense())  # type: ignore
    )
    return [new_treatment_mean, new_control_mean], [
        new_treatment_sigma,
        new_control_sigma,
    ]


def choose_arm(experiment: BayesianABSample) -> int:
    """
    Choose arm based on posterior

    Parameters
    ----------
    experiment : BayesianABSample
        The experiment data containing priors and rewards for each arm.
    """
    index = np.random.choice(len(experiment.arms), size=1)
    return int(index[0])


def update_arm_params(
    experiment: BayesianABSample,
    mus: list[float],
    sigmas: list[float],
    rewards: list[float],
    treatments: list[float],
) -> tuple[list, list]:
    """
    Update the arm parameters based on the reward type.

    Parameters
    ----------
    experiment : BayesianABSample
        The experiment data containing arms, prior type and reward
        type information.
    mus : list[float]
        The means of the arms.
    sigmas : list[float]
        The standard deviations of the arms.
    rewards : list[float]
        The rewards.
    treatments : list[float]
        Which arm was applied corresponding to the reward.
    """
    link_function = None
    if experiment.reward_type == RewardLikelihood.NORMAL:
        link_function = ContextLinkFunctions.NONE
    elif experiment.reward_type == RewardLikelihood.BERNOULLI:
        link_function = ContextLinkFunctions.LOGISTIC
    else:
        raise ValueError("Invalid reward type")

    return _update_arms(
        mus=np.array(mus),
        sigmas=np.array(sigmas),
        rewards=np.array(rewards),
        treatments=np.array(treatments),
        link_function=link_function,
        reward_likelihood=experiment.reward_type,
        prior_type=experiment.prior_type,
    )
