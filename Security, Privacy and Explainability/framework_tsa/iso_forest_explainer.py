# explainers/iso_forest_explainer.py
import shap
from sklearn.ensemble import IsolationForest

class IsolationForestExplainer:
    def __init__(self, model):
        """
        Initialize SHAP Explainer for Isolation Forest.
        :param model: Trained Isolation Forest model
        """
        self.model = model
        self.explainer = shap.TreeExplainer(model)

    def get_explanation(self, data):
        """
        Explain the given instances.
        :param instance: Input data (single sample)
        :return: SHAP values for the instance and the model expected value
        """
        return self.explainer.shap_values(data), self.explainer.expected_value
    
    def get_summary_plot(self, data, shap_values = None):
        """
        Get the summary plot for the given data.
        :param data: Input data
        :param shap_values: SHAP values for the input data
        :return: Summary plot, showing the impact of each feature on the output
        """
        if shap_values is None:
            shap_values, _ = self.get_explanation(data)
        return shap.summary_plot(shap_values, data)
    
    def get_force_plot(self, data, shap_values = None):
        """
        Get the force plot for the given data.
        :param data: Input data
        :param shap_values: SHAP values for the input data
        :return: Force plot, showing the impact of each feature on the output
        Remember that for each data row there must be a set of corresponding shap values and vice versa
        """
        if shap_values is None:
            shap_values, _ = self.get_explanation(data)
        return shap.force_plot(self.explainer.expected_value, shap_values, data)
