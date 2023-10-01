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

| Name | type | PCI DSS flag | PII flag | Sensetive data description | Business owner| Purpose | Access Owner | Comments |
|------|------|--------------|----------|----------------------------|---------------|---------|--------------|----------|

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
