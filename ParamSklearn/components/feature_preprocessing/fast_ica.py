import warnings

import sklearn.decomposition

from HPOlibConfigSpace.configuration_space import ConfigurationSpace
from HPOlibConfigSpace.hyperparameters import CategoricalHyperparameter, \
    UniformIntegerHyperparameter
from HPOlibConfigSpace.conditions import EqualsCondition

from ParamSklearn.components.base import \
    ParamSklearnPreprocessingAlgorithm
from ParamSklearn.constants import *


class FastICA(ParamSklearnPreprocessingAlgorithm):
    def __init__(self, algorithm, whiten, fun, n_components=None,
                 random_state=None):
        self.n_components = None if n_components is None else int(n_components)
        self.algorithm = algorithm
        self.whiten = whiten == 'True'
        self.fun = fun
        self.random_state = random_state

    def fit(self, X, Y=None):
        self.preprocessor = sklearn.decomposition.FastICA(
            n_components=self.n_components, algorithm=self.algorithm,
            fun=self.fun, whiten=self.whiten, random_state=self.random_state
        )
        # Make the RuntimeWarning an Exception!
        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                self.preprocessor.fit(X)
            except ValueError as e:
                if e.message == 'array must not contain infs or NaNs':
                    raise ValueError("Bug in scikit-learn: https://github.com/scikit-learn/scikit-learn/pull/2738")
                else:
                    import traceback
                    traceback.format_exc()
                    raise ValueError()

        return self

    def transform(self, X):
        if self.preprocessor is None:
            raise NotImplementedError()
        return self.preprocessor.transform(X)

    @staticmethod
    def get_properties(dataset_properties=None):
        return {'shortname': 'FastICA',
                'name': 'Fast Independent Component Analysis',
                'handles_missing_values': False,
                'handles_nominal_values': False,
                'handles_numerical_features': True,
                'prefers_data_scaled': True,
                'prefers_data_normalized': True,
                'handles_regression': True,
                'handles_classification': True,
                'handles_multiclass': True,
                'handles_multilabel': True,
                'is_deterministic': False,
                'handles_sparse': True,
                'handles_dense': True,
                'input': (DENSE, UNSIGNED_DATA),
                'output': (INPUT, UNSIGNED_DATA),
                'preferred_dtype': None}

    @staticmethod
    def get_hyperparameter_search_space(dataset_properties=None):
        cs = ConfigurationSpace()

        n_components = cs.add_hyperparameter(UniformIntegerHyperparameter(
            "n_components", 10, 2000, default=100))
        algorithm = cs.add_hyperparameter(CategoricalHyperparameter('algorithm',
            ['parallel', 'deflation'], 'parallel'))
        whiten = cs.add_hyperparameter(CategoricalHyperparameter('whiten',
            ['False', 'True'], 'False'))
        fun = cs.add_hyperparameter(CategoricalHyperparameter(
            'fun', ['logcosh', 'exp', 'cube'], 'logcosh'))

        cs.add_condition(EqualsCondition(n_components, whiten, "True"))

        return cs


