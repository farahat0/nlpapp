# to run this project # :
- open in vs code

- install dependencies from the pyproject.toml (uv) run the command *uv pip install -r pyproject.toml*

- open new terminal

- run the command *uvicorn app.main:app --reload --port 8000* to restart the fastApi server, in may take some time for the first run. wait for the message " Application startup complete "

- open new terminal and run the command *cd frontend*

- run the command *npm run dev* then it will give you local host link to open the application 

# issues you may face #
- error because of the GOOGLE_API_KEY and HF_TOKEN 