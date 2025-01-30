# explainers/ffnn_explainer.py
import shap
import numpy as np

class NnExplainer:
    def __init__(self, model, data):
        """
        initialize the explainer
        model: User supplied function or model object that takes a dataset of samples and computes the output of the model for those samples.
        data: background data the explainer will use to analyze the model's output. feed it a sample of the dataset.
        """
        self.model = model
        self.data = data
        self.explainer = shap.KernelExplainer(model, data)

    def get_explanation(self, data, samples = 50):
        """
        Get the shapley values and expected value for a single or many predictions.
        data: the rows of the data matrix to explain.
        explainer.expected_value indicates the expected output of the model.
        shap_values is an ndarray containing one shapley value (float) for each feature, for each record.
        shapley values determine how much a feature defined the final result with respect to the expected value
        """
        shap_values = self.explainer.shap_values(data, n_samples = samples)
        return shap_values, self.explainer.expected_value

    def get_force_plot(self, data, shap_values = None):
        """
        returns a force plot for the given data. If shap_values are not provided, they will be calculated.
        Remember that for each data row there must be a set of corresponding shap values and vice versa
        """
        if shap_values is None:
            shap_values, _ = self.get_explanation(data)
        return shap.force_plot(self.explainer.expected_value, shap_values, data)

# def get_regression_explainer(model, time_series, n_lags = 14):
#     """
#     Get the SHAP explainer for a regression model.
#     :param model: Trained regression model
#     :param time_series: Time series data
#     :return: SHAP explainer
#     """
# 
#     ts = time_series.sample(14)
#     scaler = MinMaxScaler(feature_range=(0, 1))
#     ts = scaler.fit_transform(ts)
# 
#     ts = np.array(ts)
#     ts = np.lib.stride_tricks.sliding_window_view(ts, window_shape=n_lags)[:-1]
#     ts = ts.reshape(ts.shape[0], n_lags)
#     explainer = shap.KernelExplainer(model, ts)
# 
#     return explainer


# def get_explanation(model, data, samples = 50):
#     """
#     Get the shapley values and expected value for a single or many predictions.
#     model: User supplied function or model object that takes a dataset of samples and computes the output of the model for those samples.
#     data: 
#     shap_values is an ndarray containing one value for each feature, for each record.
#     shapley values determine how much a feature defined the final result with respect to the expected value
#     explainer.expected_value is a float.
#     """
# 
#     
#     explainer = shap.KernelExplainer(model, data)
#     shap_values = explainer.shap_values(data, n_samples = samples)
# 
#     return shap_values, explainer.expected_value


# def get_force_plot(explainer, shap_values, time_series):
#     return shap.force_plot(explainer.expected_value, shap_values, time_series)