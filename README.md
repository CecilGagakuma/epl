# ⚽ EPL Stats Pipeline

A backend data pipeline for Premier League match data, built with Python. It loads historical match results, stores them in PostgreSQL, and serves league tables and team stats through a FastAPI service. The end goal is an event-driven system where match events are streamed through Kafka and the league table updates live as a season replays, with everything running from a single `docker compose up`. I'm building this project to learn backend and data engineering practices: clean, tested code, containerization, CI, and stream processing.

**Status:** 🚧 Work in progress. Currently setting up the project structure and CSV data loader.

**Planned stack:** Python · PostgreSQL · FastAPI · Kafka · Docker · GitHub Actions