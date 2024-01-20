# LoA Processor Script
___
This project helps to collect data from hard inventory surveys and cleans up raw data a bit.
___
### Configure Google Project
First of all, you need to set up a project in Google Cloud. 
1. Create project
2. Set up service account 
3. Get credentials for it and save json file with credentials
4. Enable Google Spreadsheet API for this project 
5. Don't forget to grant access to your Google spreadsheets for your service account

##### Now you need to set up an environment variable GOOGLE_TOKEN_PATH with path to your service account credential json path
___
### LoA
This script works in compliance with Dodo Brands Security procedures. Especially, with Assets Hard Inventory procedure.

You need a list with all departments and units of you company, you need to manage manual audits and store surveys. This scripts works with following configuration:


| Department | Unit| Leader| Survey link| Expert | Auditor	 | Expert | Auditor |
|------------|-----|-------|------------|--------|----------|--------|---------|

And you need a conventional looking survey, in this configuration: 

| Name | type | PCI DSS flag | PII cleints flag | PII employees flag | Sensetive data description | Business owner| Purpose | Access Owner | Comments |
|------|------|--------------|------------------|--------------------|----------------------------|---------------|---------|--------------|----------|

How exactly will you run hard inventory depends on you, maybe Dodo Brands once will decide to share their practices of internal security and I will attach a link to it here. I designed those procedures, but I made them for a company, so I'll pass a right of publication to Dodo Brands. 
___
### Basic preparation

```commandline
git clone https://github.com/malinborn/LoaProcessing.git

python3 -m venv LoaProcessing

cd LoaProcessing

source bin/activate

pip3 install -r requirements.txt
```
___
### Configuration
Make a copy of "config_template.json" and name it "config.json".

Fill in IDs of Google spreadsheets, where to you want to upload data. 

On a spreadsheet from those add a sheet named "LoA_raw".
___
### How to add new domain
1. Add new domain variable to Enum `LoaOptions`, keep the notation
2. Than add new option to CLI
	1. Add new statement into match-case tree
	2. Put new variable from step 1 into global variable `LOA_OPTION`
3. Add new key-value pair to config file. 
    - You should update both config and template. 
    - Here you should put an ID of your google spreadsheet, that will contain a new domain LOA 
	- Note that every domain LOA have to have its own table!
4. Go to `main.py` file and add receiving of new table ID to `build_google_service` function into match-case tree 
5. In `main.py` update `prepare_data` function with new domain. 
	- It posses two properties — departments and units
	- Keeping both empty means "each existing asset"
	- Adding a department you mean "add each asset of each unit of the department"
	- Adding a unit you mean "add each asset of the unit"
6. Done! 