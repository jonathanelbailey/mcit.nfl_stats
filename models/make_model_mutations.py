"""
1. factorize cal_data and push to new table as model_data
2. set parameters
3. select the latest season and create test_data table from it
4. select all seasons but the latest season and create training_data table from it
5. train model with xgboost and send results to db
6. generate predictions and send results to ep_model_predictions table
7. plot model results as part of kubeflow experiment


NEXT STEPS
1. turn libraries into workflows
2. create models for ep, wp, wp_spread, xyac, etc
3. generate model to beat house edge for spread, moneyline, over/under, etc
4. once house edge model is created, integrate qb impact to models
5. create model for 4th down conversion predictions
6. create dashboard to view model accuracy stats for all prediction models
7. create dashboard to interact with model for what-if analysis

WORKFLOWS

data imports
1. consult sqlalchemy to determine if fastexecutemany is constrained by memory/cpu
2. configure chunk size to see if fewer jobs are required with larger chunk sizes
3. determine best way to implement multithreading - by season and in a single pod probably
4. add a check to see if the table already exists, and has the latest data.  skip if so
5. next step in this workflow is to spawn a job to update cal_data with new information if needed
5. next, spawn a job to make the mutations to the model if cal_data has been updated and import to db
6. next, spawn a job to create the test data and training data and import to db if it makes sense
7. train the model - multithreaded?  multijob?
8. gather predictions and import to db if necessary
9. import results to database
10. plot calibration results and create artifact

This will be the template for ep, wp, wp_spread, xyac models etc
Figure out a way to update database with live results

UNIT TESTING:
1. cal_data creation was extremely painful
2. unit testing is direly needed
3. start with pytest and start with local testing
4. create a repo and deploy a jenkins server - other cicd tools are absolutely on the table
5. create a pipeline and turn the libraries into pip packages
6. deploy artifactory community edition and deploy packages to artifactory
7. when package is updated, image build pipeline is kicked off to update
8. create docker image pipeline that pulls the pip packages, builds, and pushes to the registry (artifactory?)
9. when image is updated, kubeflow experiment pipeline is kicked off to update
10. create pipeline to deploy templates to kubeflow, and kick off any experiments that depend on the pipeline

update pbp_data
1. check the code in nfl-data repo
2. port the code to python and implement a workflow that kicks off when nflscrapr-data is updated

"""
