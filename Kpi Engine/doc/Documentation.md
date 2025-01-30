
# KPI calculation engine introduction 

The KPI calculation engine is responsible for the calculation of kpis; it interacts with other parts of the system to calculate kpis. Along with the kpi engine we also have the alert monitor which has the responsibility of monitoring kpis from the machines and does soe by interaction with the kpi engine and other parts of the system as well.

## The calculation engine

The kpi calculation engine computations goes through the following steps to make a calculation

1. parameter validation  
2. semantical validation  
3. data retrieval  
4. calculating the expression


The parameter validation is handled by pydantic that can validate incoming parameters and a bit of code when necessary, for the semantic validation we have to check if the kpis requested can be calculated with a certain machine, if so then we proceed with data retrieval from the database and finally invoke the calculation engine to get the result. The dsecribed workflow is represented in the image below. 

\image html kpi-engine.png
\image latex kpi-engine.png

This workflow is used for both calculation of normal expressions and simlarly for the expressions of the alert monitoring, with some modification for the alert part.

## Alert monitoring 

The the kpi engine also features the capability of monitoring custom alerts on request and periodically perform calculations and in case fire the alerts by contacting the system to notify it.

## Communication
Interaction with other parts of the system happens using the HTTP protocol
the points exposed are 5 of which only 4 are meant for external communications while 1 is meant for internal ones(as in the picture above):

- **calculate** used by other parts of the system to ask for custom calculations.  
- **add\_alert** which adds a new alert to be monitored.  
- **remove\_alerts** which can remove specified alerts from the monitoring  
- **get\_all\_alerts** gives all the currently monitored alerts.  
- **alert** which is used as an internal communication between the alert monitor and the kpi engine to ask for custom calculations on the alerts expressions

All the endpoints are documented and can be tried at the address [localhost:8000/docs](localhost:8000/docs) please ensure that the docker container of the kpi engine is running and also the docker container for api layer is running and if you want to try out the apis also the containers for database and knowledge base.


## System overview

\image html kpi-engine-system.png
\image latex kpi-engine-system.png

In the image above we can see a representation of the various elements of the system we talked about in the previous parts.

The normal flow during the interaction in the system is that when some calculation is needed from a component in the system it is request through the **calculate** endpoint. As for the laerts we have the corresponding endpoints to add/remove/get the alerts that the system is currently monitoring, and then using the corresponding external endpoint the system will notify the alerts that are to be fired.

## Usage
Note: you need Docker installed, if not please install it.

To start the system KPI engine directory, from there use the following command inside the KPI engine directory: 

```bash
docker-compose –-build -d
```
after that you can visit the address [localhost:8000/docs](localhost:8000/docs) from your browser and can try out the apis.

### technologies used

For this part we used different technologies, in particular we have a  [Docker](https://www.docker.com/) container to make everything easy to run on different machines. All the requests are handled using [FastAPI](https://fastapi.tiangolo.com/) and [Pydantic](https://docs.pydantic.dev/latest/) which proved useful, their combination allowed us to easily write a documentation of the apis to interact with other parts and also Pydantic can take care of most of the parameter validation thanks to it’s models while fastapi is very flexible and reliable.
To realize the alert monitor we decided to use [APScheduler](https://apscheduler.readthedocs.io/en/3.x/) which allows very flexible scheduling of jobs as well as a lot of options for job execution for different kind of tasks and need for storing the jobs to launch.

## Code organization

Here we have a tree view to help understand the organization of code and how things are done.

```
KPI engine
├── app
│   ├── Alert_Monitor
│   │   ├── Tests
│   │   └── alert_monitor.py
│   ├── Database
│   │   └── Database_interface.py
│   ├── Documentation.md
│   ├── KPI_engine
│   │   ├── EngineCalculation
│   │   │   └── calculation_engine.py
│   │   └── Tests
│   ├── Knowledge_base
│   │   └── knowledge_base_interface.py
│   ├── Tests
│   │   ├── test_alert_monitor.py
│   │   ├── test_api.py
│   │   └── test_engine_kpi.py
│   ├── main.py
│   ├── models
│   │   ├── alert_requests.py
│   │   └── calculation_request.py
│   ├── run_tests.sh
│   └── utils
│       ├── calculation_utils.py
│       └── utils.py
├── locustfile.py
├── docker-compose.yml
├── requirements.txt
└── stress_load_test.py
```

This part is more technical and is thought to help navigate the code base of the kpi engine, for this reason when a path to something is specified it is assumed to start from the kpi engine folder. To avoid redundancy we are gonna explain what the most important files contain and then you can also view the code yourself which contains comments and other thing help understanding better how the system works.

- The *app/Database* and *app/Knowledge\_base* folders contain the utilities used to interact with the knowledge base and database respectively and are used by the calculation engine to retrieve data and do semantical validation and also the alert monitor uses the knowledge base to do also semantical checking when adding new alerts to monitor.

- Inside the *app/KPI\_engine/EngineCalculation* is the calculation engine code, for the logic please refer to the Calculation logic section since it is more articulate and needs more explanations.

- The *app/models* folder contains the pydantic models definitions used to validate parameters and generate the documentation, too understand better their usage you can see the code in the relative files which is quite simple or read the summary in the dedicated section.

- *main.py* contains all the endpoint definitions explained in the previous section.

- *app/Alert\_monitor.py* contains the alert monitor code, please visit the dedicated section for more details.

- *app/utils* contains utility files that we used to realize other components of the engine.

- *stress\_load\_test.py* contains the code used to test the calculation capabilities of the engine


- Finally to test the code we have the *Tests* folder which contains our unit tests for the kpi engine various parts.

Finally we also have a requirements.txt file containing all the dependencies needed, Dockerfile and docker-compose.yml file used to setup our docker container, and the file used to generate this documentation.

### Load testing

To test the capabilities we also decided to do some load testing, for this part we decide to use [locust](https://locust.io/). 
The framework allows us to send multiple request with settings like: 
-  Number of users: upper bound on the number of users simulated.  
-  Ramp up: Number of users simulated added by second (until the upper bound is reached).
-  Run time: Total time of test.  
- Task: It is possible to describe task that every user can perform.

It is possible to get also quantitative graphs of  data about KPI the engine performances according to number of users. 

For our tests we also tried the alert monitor using multiple parallel users, each user can pick a random action between calculate,add,remove and get alerts, such test code is in the stress_load_test.py file.

### Resource consumption

using docker can be heavy both from disk usage and memory usage however such problem is counterbalanced by the possibility offered by using the containers, at normal pace with no data the engine uses 165 mb of memory ram and has a cpu usage of 1.7%  so it’s not too much considered the capacities of normal machines.