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
    - Role based access control mitigates the problems since the API to access the agent can be accessed only with user roles, Implemented with:
        - Token by generating random strings using JWTs with strong signing keys
        - Stored hashed tokens in the database alongside `<user_id,token_hash,expiration,created_at,last_used>`
        - Tokens are validated by checking the database (matched hash and before expiration).
        - Planning to add rate limit.
    - For inversion, since the model is quite stupid and has a small context, it is difficult to release problematic information
    - User input is getting sanitized and controlled before being fed into the agent.

Structure of token table

|id| user_id  | token_hash  | expiration  | created_at  | last_used  |
|---|---|---|---|---|---|
|1|101|5e884898da28047151d0e56f8dc629277...|2024-12-01 10:00:00|2024-11-25 10:00:00|2024-11-25 12:00:00|
|2|102|2b9e64d8a813a0ecba3459a53a75d2f8c...|2024-12-02 11:00:00|2024-11-25 11:00:00|2024-11-25 13:00:00|
|3|103|a3f390d88e4c41f2747bfa2f1b5f87dbd...|2024-12-03 12:00:00|2024-11-25 12:00:00|NULL|
|4|104|98c55da5dc06709e6a4777ad2d6c1234f...|2024-12-04 13:00:00|2024-11-25 13:00:00|2024-11-25 14:00:00|
|5|105|d2d0714f014a9784047eaeccf956520045...|2024-12-05 14:00:00|2024-11-25 14:00:00|NULL|

### 1.2 Secure Development Practices
- **Findings**:
    - Input validation was ensured for all user-facing APIs.
- **Actions Taken**: 
    - Implemented input sanitization and validation for all forms of user input.


### 1.3 SQL Queries
- **Review Scope**: Evaluated security of the sql interfaces of the system
- **Findings**:
    - Non parameterized query pose a risk for possible attacks through SQLInjection.
- **Actions Taken**: 
    - Parameterized all queries and handled them through `psycopg2`
    - Handled exceptions caused by malicious input


## 2. Privacy Analysis

### 2.1 Data Collection & Storage Review
- **Review Scope**: Evaluated how user data is collected, stored, and processed by the system.
- **Findings**:
    - None, yet. All data is anonymized. User data is encrypted thanks to the authentication protocol implemented
- **Actions Taken**:
    - Implemented data minimization principles to limit the amount of PII collected.
    - Introduced regular audits of data access and usage (checking other groups work).

### 2.2 Authentication protocol
- **Actions Taken**:
    - Implemented data minimization principles to limit the amount of PII collected.
    - Implemented authentication and RBAC through user tokens.

## 3. Explainability Analysis

### 3.1 LLM Interpretability
- **Findings**:
    - The model used in `GRAPHrag123_final.ipynb` is a text2text generative model. Since it is a deep neural network with attention mechanisms, it is a black-box model.
    - Context based responses used for the new Mistral model increase interpretability.
- **Actions Taken**:
    - Implemented `bertviz` library to interactively visualize how the attention mechanism works for this agent.

### 3.2 Time series forecasting Interpretability
- **Findings**:
    - The model used for time series forecasting is a feedforward neural network. It is a black box model.
- **Actions Taken**:
    - Implemented shapley values based interpretability to explain feature importance when the model makes predictions. Needs to be integrated with team 3 work.

### 3.3 Anomaly detection Interpretability
- **Findings**:
    - The model used for anomaly detection is an isolation forest. Explanations for its prediction would be well received.
- **Actions Taken**:
    - Implemented shapley values based interpretability to explain feature importance when the model makes predictions. Needs to be integrated with team 3 work.

### 3.4 Alerts Interpretability
- **Findings**:
    - Alerts computed by the kpi engine do not include the expressions that were calculated to produce them. 
- **Actions Taken**:
    - The content of the object returned by the `alert` call now includes the expression field.

## Conclusion

The security, privacy, and explainability analyses have identified several areas of improvement, all of which have been addressed with actionable mitigation strategies. This process ensures that the repository adheres to best practices and provides transparency for users while minimizing risks to security and privacy.

## Authors

Selorm and Yuri