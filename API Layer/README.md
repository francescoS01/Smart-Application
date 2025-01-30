# API Layer - Python Flask Server

## Requirements
Docker is required to run the server. If you don't have Docker installed, you can install it from [here](https://docs.docker.com/get-docker/).

## Usage
To build the docker image and run the server, execute the following command from the root directory of the project:

```
docker build -t swagger_server -f "./API Layer/Dockerfile" .
```

To run the server, execute:

```
docker-compose -f "./API Layer/docker-compose.yml" up -d
```

To build and run the server in one command, execute from the root:

```
docker-compose -f "./API Layer/docker-compose.yml" up -d --build
```

Docker compose can be used also in the API Layer directory with:

```
docker-compose up -d --build
```

Incoming requests are handled on port 443, requests on port 80 are redirected to 443.

The API can be contacted within the docker network using "api-layer" as hostname (since it is its service name)

You can access an interactive Swagger UI for the interface at:

```
https://localhost:443/ui/
```

Since requests on port 80 are redirected to 443, you can also access the Swagger UI at:

```
http://localhost/ui/
```

That allows to authenticate and test API endpoints with custom parameters.

Your Swagger definition lives here:

```
https://localhost:443/swagger.json
```

## Authentication

Authentication is done using a JWT token that can be obtained by calling the /user/login endpoint with correct credentials (username and password in the headers).
If done from the Swagger UI, only the part following Bearer should be passed to the authorize button(Bearer is automatically added). Otherwise, the full token should be passed in the Authorization header.
An example of the authentication process is available in the "Demo" directory.

## Testing

To launch the integration tests, use pytest.
Use either
```
docker exec -it apilayer-api-layer-1 sh
pytest
```
to launch an interactive shell attached to the container and launch the test inside it, or
```
docker exec apilayer-api-layer-1 pytest
```
to launch the test from outside (without pretty printing).

## Documentation

A documentation file is available in the API Layer directory, named "OpenAPI Spec.yaml". It contains the OpenAPI specification of the API.
It can be rendered using the online Swagger Editor (https://editor.swagger.io/).
