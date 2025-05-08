# Insulin Pump and Apple Watch data parser

These scripts parse and combine Apple Watch data exports with Tandem TSlim X2 data exports and save the result as a HuggingFace Dataset.

## Getting Started

Note: We like `uv` for managing Python environments, so we use it here. If you don't want to use it, simply skip the `uv` installation and leave `uv` off of your shell commands.

### 1. Create a virtual environment

First, [install](https://github.com/astral-sh/uv) `uv` for Python environment management.

Then create and activate a virtual environment:

```shell
uv venv env_t1d_dataset
source env_t1d_dataset/bin/activate
```

### 2. Install the prerequisite packages

```shell
uv pip install -r requirements.txt
```

### 3. Download your pump data

On the TSlim X2 web portal, select up to 28 days at a time in reports and click `print`, then `save data` to download a CSV file with your pump data.

Unfortunately, I'm not aware of any better way than to go one month at a time. Complete this download for all of your data. It's OK if some time ranges overlap or if there are duplicates - the parser will deduplicate data for you.

Save all of the CSV files into a single directory.

### 4. Download your Apple Watch data

Open up the Apple Health app and click your profile on the top right on the summary page. Scroll down to the bottom and hit `Export All Health Data`. Download this xml file onto your computer.

### 5. Run the parser

To run the parser:

```shell
python dataset.py --pump_ds_dir /path/to/pump --apple_ds_file /path/to/apple_health_export/export.xml --save_file /path/to/hf_dataset
```

This will process the data and save the result as a HuggingFace dataset.