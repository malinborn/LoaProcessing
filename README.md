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

```commandline
python3 -m venv loa
source loa/bin/activate

cd loa
pip3 install -r requirements.txt
```
