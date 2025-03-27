import numpy as np

from ..mab.sampling_utils import sample_beta_binomial, sample_normal
from ..schemas import ArmPriors, RewardLikelihood
from .schemas import ABExperimentSample, ArmResponse


def update_arm_beta_binomial(
    alpha: float,
    beta: float,
    successes: int,
    failures: int,
) -> tuple[float, float]:
    """
    Update the alpha and beta parameters of the Beta distribution.

    Parameters
    ----------
    alpha : int
        The alpha parameter of the Beta distribution.
    beta : int
        The beta parameter of the Beta distribution.
    successes : int
        The number of successes.
    failures : int
        The number of failures.
    """
    return alpha + successes, beta + failures


def update_arm_normal(
    mu: float, sigma: float, rewards: list[float]
) -> tuple[float, float]:
    """
    Update the mean and standard deviation of the Normal distribution."

    Parameters
    ----------
    mu : float
        The mean of the Normal distribution.
    sigma : float
        The standard deviation of the Normal distribution.
    rewards : list[float]
        The rewards.
    """
    n = len(rewards)
    sigma_llhood = np.std(rewards) / np.sqrt(n)
    denom = sigma_llhood**2 + sigma**2

    new_sigma = sigma_llhood * sigma / np.sqrt(denom)

    new_mu = (mu * sigma_llhood**2 + np.mean(rewards) * sigma**2) / denom

    return new_mu, new_sigma


def choose_arm(experiment: ABExperimentSample) -> int:
    """
    Choose arm based on posterior

    Parameters
    ----------
    experiment : ABExperimentSample
        The experiment data containing priors and rewards for each arm.
    """
    if (experiment.prior_type == ArmPriors.BETA) and (
        experiment.reward_type == RewardLikelihood.BERNOULLI
    ):
        alphas = np.array([arm.alpha for arm in experiment.arms])
        betas = np.array([arm.beta for arm in experiment.arms])

        return sample_beta_binomial(alphas=alphas, betas=betas)

    elif (experiment.prior_type == ArmPriors.NORMAL) and (
        experiment.reward_type == RewardLikelihood.NORMAL
    ):
        mus = np.array([arm.mu for arm in experiment.arms])
        sigmas = np.array([arm.sigma for arm in experiment.arms])
        # TODO: add support for non-std sigma_llhood
        return sample_normal(mus=mus, sigmas=sigmas)
    else:
        raise ValueError("Prior and reward type combination is not supported.")


def update_arm_params(
    arm: ArmResponse,
    prior_type: ArmPriors,
    reward_type: RewardLikelihood,
    rewards: list[float],
) -> tuple[float, float]:
    """
    Update the arm parameters based on the reward type.

    Parameters
    ----------
    arm : ArmResponse
        The arm data.
    prior_type : ArmPriors
        The prior type.
    reward_type : RewardLikelihood
        The reward type.
    rewards : list[float]
        The rewards.
    """
    if reward_type == RewardLikelihood.BERNOULLI:
        successes = int(sum(rewards))
        failures = len(rewards) - successes

        if (not arm.alpha) or (not arm.beta):
            raise ValueError("Beta prior requires alpha and beta")

        return update_arm_beta_binomial(arm.alpha, arm.beta, successes, failures)

    elif reward_type == RewardLikelihood.NORMAL:
        if (not arm.mu) or (not arm.sigma):
            raise ValueError("Normal prior requires mu and sigma")
        return update_arm_normal(arm.mu, arm.sigma, rewards)

    else:
        raise ValueError("Reward type not supported.")
