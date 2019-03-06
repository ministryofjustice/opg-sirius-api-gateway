# Local Container mock for OPG Sirius API Gateway

## Local development of the OPG API Gateway container

To create a virtual environment to work in
```bash
cd opg-sirius-api-gateway
python3 -m venv api-gateway
```

Activate the virtual environment
```bash
. api-gateway/bin/activate
```

Install the pip requirements
```bash
pip install -r docker/api-gateway/requirements.txt
```

### Helpful Commands

docker build -t test/opg-sirius-api-gateway .
docker run -v /var/run/docker.sock:/var/run/docker.sock -ti test/opg-sirius-api-gateway:latest
