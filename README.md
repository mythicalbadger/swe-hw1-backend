# Software Engineering Homework 1 Backend

This is the backend component of a webapp that allows employees at a company to request leave days from HR.
## Setup
### Libraries
The backend was built using Tiangolo's [FastAPI](https://fastapi.tiangolo.com/) and [SQLModel](https://sqlmodel.tiangolo.com/).
### Dependencies
I'm using Python version `3.12.0`. Dependencies can be found in `pyproject.toml`. Using [Poetry](https://python-poetry.org/), one can simply run
```shell
poetry install
```
to fetch all dependencies required.
### Environment Variables
The project allows the following environment variables to be set in `/src/.env`
- `DATABASE_USER`: the user of the database (by default, `"root"`)
- `DATABASE_PASSWORD`: the password for the user (by default, `"hardpass"`, which is hands down the best password to have ever existed)
- `DATABASE_DB`: the name of the database (by default, `"leave_request"`
- `DATABASE_PORT`: the port used to connect to database (by default, `"3306"`)
## Structure
Based on [Structuring FastAPI application with multiple services using 3-tier design pattern](https://viktorsapozhok.github.io/fastapi-oauth2-postgres/). Pretty much
- API routes can be found in `routers/`
- Database models can be found in `models/`
- Pydantic models used for routers can be found in `schemas/`
- Business/database logic can be found in `services/`
- Utility related methods can be found in `utils/`
- Database connection info can be found in `database.py`
