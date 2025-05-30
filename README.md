# Findex Vis

Findex Vis is a web application that visualizes machine learning model predictions on financial survey data. It features a FastAPI backend and an HTML/CSS/D3.js frontend. Machine learning outputs are generated onto mounted drive and made available for visualization.

## Project Overview

Data is retrieved from [WorldBank.org](https://www.worldbank.org/en/publication/globalfindex/Data).  

FastAPI Backend: Serves data and APIs for the frontend.
Frontend with D3.js: Interactive visualizations of ML model predictions.
Containerized Deployment: The entire application is containerized using Docker, ready for minikube dev deployment.

## Installation and Setup
1) Create a free account on [WorldBank.org](https://microdata.worldbank.org/index.php/catalog/4607) by clicking on register at the top right of the page.
2) Verify the account creation by clicking on the account creation link sent to the email used to sign up
3) After verifictation go to this link [WorldBank.org](https://microdata.worldbank.org/index.php/catalog/4607) and select GET MICRODATA 
4) Fill in the purpose as "Educational Purpose" in the "Application for Access to a Public Use Data" form and press submit 
5) Download the file shown in the picture below
  ![World Bank Data](images/world_bank_data.jpeg)
6) A backup link to download the dataset is available at the class [Teams shared folder](https://gtvault.sharepoint.com/:x:/s/CSE6242663/Edc7pw-ekURMlST5YilCRPMBJnK70cfPxsq4Cj6Bc-jHxw?e=1qQZEg) (GA Tech .edu account is required)

# Findex Visualization Dashboard

This project sets up a visualization dashboard that uses World Bank data and a decision tree model to display financial inclusion insights.
Before starting, ensure the following tools are installed and working:

- [Docker](https://docs.docker.com/get-docker/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)

You can check if they are installed by running these commands:
```bash 
docker info
minikube -version
```
Then run these commands and follow the steps:
```bash
docker ps
minikube start --driver=docker 
cd findex_vis
mv user_data data
cp findex2021_micro_world_139countries.csv data/ (File from World Bank site)

ls -l data (verify these files are present)
    findex2021_micro_world_139countries.csv (File from World Bank)
    ft2verbose.json
    world_countries.json

On Windows, at root folder findex_vis/
deploy_win.bat

On MacOS, at the root folder findex_vis/
sh deploy_mac.sh
```

The script will run and spin up multiple terminals to run the app and also launch the dashboard. 

Scroll down on the dashboard to the bottom and choose Default Decision Tree and click prediction 
This will run the model and generate the files needed by the dashboard
Once this process is done you can refresh the screen and the fields should populate now.

The dashboard requires these files to be present in the /data in the root level to work correctly 
1) ft2verbose.json
2) world_countries.json
3) metrics_by_cluster.json
4) metrics_by_countries.json


## Dashboard 
![Image of the running dashboard](images/dashboard.jpeg)


## Helpful Commands and resources
```bash
kubectl logs -l app=mlapi
kubectl logs -l app=flask-app
kubectl get pods
kubectl get services
kubectl describe pod <pod-name> #see why pod is failing outward
kubectl logs <pod-name> #see why pod fail inward
kubectl logs deployment/mlapi -f
```
