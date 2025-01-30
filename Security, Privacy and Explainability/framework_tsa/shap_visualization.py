from shap import Explanation, waterfall_plot, summary_plot

def plot_ffnn_waterfall(shap_values, base_value, forecast, feature_names, instance):
    """
    Visualize FFNN decision using a waterfall plot.
    :param shap_values: SHAP values for the instance
    :param base_value: Base value (mean output of background data)
    :param forecast: Predicted value for the instance
    :param feature_names: List of feature names
    :param instance: Input feature values
    """
    explanation = Explanation(
        values=shap_values, base_values=base_value,
        data=instance, feature_names=feature_names
    )
    waterfall_plot(explanation)

def plot_iso_forest_waterfall(shap_values, anomaly_score, feature_names, instance):
    """
    Visualize Isolation Forest decision using a waterfall plot.
    :param shap_values: SHAP values for the instance
    :param anomaly_score: Anomaly score for the instance
    :param feature_names: List of feature names
    :param instance: Input feature values
    """
    explanation = Explanation(
        values=shap_values, base_values=0,
        data=instance, feature_names=feature_names
    )
    waterfall_plot(explanation)

def plot_summary(shap_values, data, feature_names):
    """
    Visualize feature contributions for all instances.
    :param shap_values: SHAP values for the dataset
    :param data: Input data
    :param feature_names: List of feature names
    """
    summary_plot(shap_values, data, feature_names=feature_names)
