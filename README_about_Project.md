# AI Supply Chain Risk Intelligence Platform

## Project Overview

The **AI Supply Chain Risk Intelligence Platform** is an end-to-end data analytics application designed to help organizations monitor and improve supply chain performance. The platform transforms raw supply chain transaction data into meaningful business insights through data cleaning, feature engineering, business intelligence dashboards, and interactive visualizations.

The project simulates a real-world enterprise analytics platform used by retail and logistics companies such as Walmart, Amazon, or FedEx to analyze sales performance, customer behavior, shipping efficiency, and operational risks.

---

# Business Problem

Modern supply chain organizations process thousands of customer orders every day. Business managers often struggle to answer important questions such as:

* Which products generate the highest revenue?
* Which regions experience the most delivery delays?
* Which shipping method performs the best?
* Which customers contribute the highest profit?
* Which products are causing financial losses?
* What operational improvements should be prioritized?

Analyzing thousands of transaction records manually is time-consuming and inefficient.

This project provides a centralized analytics platform that helps decision-makers answer these questions using data visualization and business intelligence.

---

# Project Objectives

* Clean and preprocess raw supply chain data.
* Perform feature engineering to generate meaningful business features.
* Store processed data in a MySQL database.
* Perform exploratory data analysis (EDA).
* Build interactive dashboards using Streamlit.
* Generate automated business insights and recommendations.
* Provide an easy-to-use decision support platform for managers.

---

# Dataset

**Dataset:** DataCo Smart Supply Chain Dataset

The dataset contains approximately **180,000 supply chain transactions** including:

* Customer Information
* Product Information
* Order Details
* Shipping Information
* Sales
* Profit
* Delivery Status
* Geographic Information
* Markets and Regions

---

# Project Architecture

```text
                   Raw Dataset
                        │
                        ▼
             Data Cleaning Pipeline
                        │
                        ▼
            Feature Engineering Pipeline
                        │
                        ▼
              Processed Dataset (CSV)
                        │
                        ▼
                  MySQL Database
                        │
                        ▼
            Business Analytics Engine
                        │
                        ▼
            Streamlit Dashboard
                        │
                        ▼
       Business Insights & Recommendations
```

---

# Technologies Used

| Category              | Technologies              |
| --------------------- | ------------------------- |
| Programming Language  | Python                    |
| Data Analysis         | Pandas, NumPy             |
| Database              | MySQL                     |
| Visualization         | Plotly                    |
| Dashboard             | Streamlit                 |
| Database Connectivity | SQLAlchemy, PyMySQL       |
| Environment           | Python Dotenv             |
| Development           | VS Code, Jupyter Notebook |

---

# Project Workflow

## Step 1 – Data Collection

The project starts by loading the DataCo Smart Supply Chain dataset.

---

## Step 2 – Data Cleaning

The cleaning pipeline performs:

* Missing value handling
* Duplicate removal
* Data type correction
* Invalid value handling
* Outlier detection
* Outlier treatment using capping
* Data quality validation

---

## Step 3 – Feature Engineering

Several business-oriented features are created, including:

* Order Year
* Order Month
* Order Quarter
* Weekday
* Delay Days
* Profit Margin
* Profit Category
* Loss Order Indicator
* Discount Band
* Shipping Performance
* Late Delivery Risk

---

## Step 4 – MySQL Storage

Instead of reading the CSV repeatedly, the cleaned dataset is stored in a MySQL database for:

* Faster querying
* Better organization
* Improved scalability
* Easier integration with dashboards

---

## Step 5 – Business Analytics

The platform performs analysis on:

* Revenue
* Profit
* Orders
* Customers
* Products
* Categories
* Markets
* Countries
* Shipping Modes
* Delivery Performance
* Customer Segments
* Fraud Indicators
* Discount Analysis

---

## Step 6 – Interactive Dashboard

The processed data is visualized using Streamlit through multiple dashboard pages.

---

# Dashboard Features

## Executive Dashboard

Displays high-level business KPIs:

* Total Revenue
* Total Profit
* Total Orders
* Total Customers
* Average Order Value
* Profit Margin
* Late Delivery Rate
* Loss Order Rate
* Fraud Rate
* Average Shipping Days

---

## Sales & Profitability Dashboard

Analyzes:

* Monthly Revenue
* Monthly Profit
* Profit vs Loss Transactions
* Discount Analysis
* Loss-Making Products

---

## Products & Categories Dashboard

Displays:

* Top Categories
* Top Products
* Revenue by Category
* Category Performance
* Revenue vs Delivery Risk

---

## Customer Analytics Dashboard

Shows:

* Customer Segments
* Customer Revenue
* Top Customers
* Customer Distribution
* Customer Value Analysis

---

## Shipping & Delivery Dashboard

Provides insights into:

* Shipping Modes
* Late Deliveries
* Average Shipping Time
* High-Risk Regions
* Delivery Performance

---

## Geographic Analysis Dashboard

Displays:

* Revenue by Country
* Revenue by Market
* Customer Location Map
* Geographic Sales Distribution

---

## Business Insights Dashboard

Automatically generates business insights such as:

* Best performing products
* Highest revenue markets
* Highest risk regions
* Most profitable categories
* Shipping performance
* Discount impact

---

## Data Explorer

Allows users to:

* Search records
* Filter data
* Explore transactions
* Download filtered datasets

---

# Key Business Insights

The platform helps answer questions such as:

* Which market generates the highest revenue?
* Which shipping mode causes the highest delays?
* Which customer segment contributes the most revenue?
* Which products generate losses?
* Which discount levels reduce profitability?
* Which regions require operational improvements?

---

# Project Outcomes

After completing the project, the platform provides:

* Clean and reliable supply chain data.
* Automated business performance analysis.
* Interactive dashboards for decision-making.
* Actionable business insights.
* Operational recommendations.
* Faster access to business metrics.
* Improved understanding of supply chain performance.

---

# Future Enhancements

The next phase of the project will include:

* Machine Learning model for predicting late deliveries.
* SHAP explainability for model predictions.
* Generative AI chatbot for natural language business queries.
* Retrieval-Augmented Generation (RAG) for intelligent document-based question answering.
* Real-time dashboard updates using streaming data.

---

# Folder Structure

```text
AI_Supply_Chain_Risk_Platform/
│
├── app.py
├── setup_project.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── src/
│   ├── data_pipeline.py
│   ├── database.py
│   └── business_insights.py
│
└── .env
```

---

# How to Run the Project

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure MySQL

Update the `.env` file with your MySQL credentials.

### 3. Place the Dataset

Copy the **DataCo Smart Supply Chain Dataset** into:

```text
data/raw/
```

### 4. Run the Data Pipeline

```bash
python setup_project.py
```

### 5. Launch the Dashboard

```bash
streamlit run app.py
```

---

# Author

**Akshay Kumar Nagabandi**

Master's in Data Science
University of Maryland, Baltimore County (UMBC)

---

# License

This project was developed for educational purposes as part of a graduate-level data science course.
