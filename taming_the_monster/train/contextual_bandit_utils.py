# -*- coding: utf-8 -*-
import numpy

from taming_the_monster.train import model_utils


def add_model(
    model, contextual_bandit, possible_actions, chosen_actions, Y, weights,
    min_probs,
):
    """TODO"""
    model_choices = _get_model_choices(
        model=model,
        possible_actions=possible_actions,
    )
    expected_reward = _get_expected_reward(
        model_choices=model_choices,
        possible_actions=possible_actions,
        chosen_actions=chosen_actions,
        Y=Y,
        weights=weights,
    )
    scaled_regret = _get_scaled_regret(
        expected_regret=max(
            policy['expected_reward'] - expected_reward
            for policy in contextual_bandit
        ),
        min_probs=min_probs,
    )
    variance_coefficients = _get_variance_coefficients(
        contextual_bandit=contextual_bandit,
        possible_actions=possible_actions,
        scaled_regret=scaled_regret,
        min_probs=min_probs,
        model_choices=model_choices,
    )
    if variance_coefficients['D'] > 0:
        return _rescale_probability(
            contextual_bandit=contextual_bandit + [
                {
                    'expected_reward': expected_reward,
                    'probability': 0.0,
                    'model': '',
                },
            ],
        )
    else:
        return contextual_bandit


def _get_model_choices(model, possible_actions):
    """TODO"""
    return [
        numpy.argmax(model_utils.score_actions(X=actions, model=model))
        for actions in possible_actions
    ]


def _get_expected_reward(
    model_choices, possible_actions,
    chosen_actions, Y, weights,
):
    """TODO"""
    num_examples, _, _ = possible_actions.shape
    return numpy.sum(
        reward * weight
        for model_choice, actions, chosen_action, reward, weight in zip(
            model_choices,
            possible_actions,
            chosen_actions,
            Y,
            weights,
        )
        if actions[model_choices] == chosen_action
    ) / num_examples


def _get_scaled_regret(expected_regret, min_probs):
    """TODO
    Explained in OP under Algorithm 1
    """
    return expected_regret / (100 * numpy.average(min_probs))


def _get_variance_coefficients(
    contextual_bandit, possible_actions, scaled_regret, min_probs,
    model_choices,
):
    """TODO"""
    model_variances = _get_model_variances(
        contextual_bandit=contextual_bandit,
        model_choices=model_choices,
        possible_actions=possible_actions,
        min_probs=min_probs,
    )
    average_variance = numpy.average(model_variances)
    return {
        'V': average_variance,
        'S': numpy.average(numpy.power(model_variances, 2)),
        'D': average_variance - (
            scaled_regret + numpy.average(
                [len(actions) for actions in possible_actions],
            )
        ),
    }


def _get_model_variances(
    contextual_bandit, model_choices, possible_actions, min_probs,
):
    """TODO"""
    return [
        1. / max(
            sum(
                policy['probability']
                for policy, model_choice in zip(
                    contextual_bandit,
                    model_choices,
                )
                if numpy.argmax(
                    model_utils.score_actions(
                        X=actions,
                        model=policy['model'],
                    ),
                ) == model_choice
            ),
            min_prob,
        )
        for actions, min_prob in zip(possible_actions, min_probs)
    ]


def _rescale_probability(contextual_bandit):
    """TODO"""
    total_weight = sum(policy['probability'] for policy in contextual_bandit)
    return [
        {
            'expected_reward': policy['expected_reward'],
            'probability': policy['probability'] / total_weight,
            'model': policy['model'],
        }
        for policy in contextual_bandit
    ]
