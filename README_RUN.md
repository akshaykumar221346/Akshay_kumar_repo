# AI Supply Chain Risk Intelligence Platform

## Folder structure

```text
AI_Supply_Chain_Risk_Platform/
│
├── app.py
├── setup_project.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py
│   ├── database.py
│   └── business_insights.py
│
├── notebooks/
│   ├── 01_data_pipeline.ipynb
│   ├── 02_database.ipynb
│   ├── 03_business_insights.ipynb
│   ├── 04_streamlit_app.ipynb
│   └── 05_setup_and_run.ipynb
│
└── data/
    ├── raw/
    └── processed/
```

## VS Code setup

1. Extract this project folder.
2. Open VS Code.
3. Select **File > Open Folder**.
4. Select `AI_Supply_Chain_Risk_Platform`.
5. Open the VS Code terminal.

## Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

When PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
python -m venv .venv
.venv\Scripts\activate
```

## Install packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configure MySQL

1. Start MySQL Server.
2. Open MySQL Workbench.
3. Confirm that your root username and password work.
4. Copy `.env.example` and rename the copy to `.env`.
5. Put your actual MySQL password in `.env`.

Example:

```text
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_actual_password
MYSQL_DATABASE=supply_chain_db
```

The Python setup script creates the database automatically.

## Add the dataset

You have two choices.

### Automatic Kaggle download

Run the setup command. `kagglehub` downloads the DataCo dataset automatically.

### Manual dataset

Place this file inside `data/raw/`:

```text
DataCoSupplyChainDataset.csv
```

## Run the complete project

```bash
python setup_project.py
```

This command:

1. Loads the raw dataset.
2. Cleans missing and invalid values.
3. Detects and reports outliers.
4. Creates feature-engineered columns.
5. Saves the processed CSV.
6. Creates the MySQL database.
7. Loads the processed data into MySQL.
8. Creates database indexes.

Then run:

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Notebook order

Open notebooks in this order:

1. `01_data_pipeline.ipynb`
2. `02_database.ipynb`
3. `03_business_insights.ipynb`
4. `04_streamlit_app.ipynb`
5. `05_setup_and_run.ipynb`

The `.py` files are the actual application modules. The notebooks are study and execution versions divided into logical cells.
