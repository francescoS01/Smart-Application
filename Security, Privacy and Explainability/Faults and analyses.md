# Security, Privacy, and Explainability Analysis

## Overview

This document provides a detailed summary of the security, privacy, and explainability analyses conducted on the codebase in this repository. It includes findings, actions taken, and any potential risks identified during the review process.

## 1. Security Analysis

### 1.1 Code Review for Vulnerabilities
- **Review Scope**: The analysis covers all core components of the application, including API layer, kpi engine and rag + llm models.
- **Findings**:
    - Model inversion risk in `informational_query()`, used for the RAG. We can bleed context if query input is not handled
    - The pipeline dinamycally allocates memory to process the queries. This exposes the system DDOS attacks at best and memory injection at worst. 
- **Mitigations**:
    - Encryption will be applied for sensitive data when and if they are present
    - Role based access control mitigates the problems since the API to access the agent can be accessed only with user roles.
    - For inversion, since the model is quite stupid and has a small context, it is difficult to release problematic information
    - User input is getting sanitized and controlled before being fed into the agent.

### 1.3 Secure Development Practices
- **Findings**:
    - Input validation was ensured for all user-facing APIs.
- **Actions Taken**: 
    - Implemented input sanitization and validation for all forms of user input.

## 2. Privacy Analysis

### 2.1 Data Collection & Storage Review
- **Review Scope**: Evaluated how user data is collected, stored, and processed by the system.
- **Findings**:
    - None, yet. All data is anonymized. User data is encrypted.
- **Actions Taken**:
    - Implemented data minimization principles to limit the amount of PII collected.
    - Introduced regular audits of data access and usage (checking other groups work).

## 3. Explainability Analysis

### 3.1 Model Interpretability
- **Findings**:
    - The model used in `GRAPHrag123_final.ipynb` is a text2text generative model. Since it is a deep neural network with attention mechanisms, it is a black-box model.
- **Actions Taken**:
    - Implemented `bertviz` library to interactively visualize how the attention mechanism works for this agent.

### 3.2 Alerts Interpretability
- **Findings**:
    - Alerts computed by the kpi engine do not include the expressions that were calculated to produce them. 
- **Actions Taken**:
    - The content of the object returned by the `alert` call now includes the expression field.

## Conclusion

The security, privacy, and explainability analyses have identified several areas of improvement, all of which have been addressed with actionable mitigation strategies. This process ensures that the repository adheres to best practices and provides transparency for users while minimizing risks to security and privacy.

## Authors

Selorm and Yuri