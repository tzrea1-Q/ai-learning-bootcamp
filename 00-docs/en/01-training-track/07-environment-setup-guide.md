# Environment Setup Guide

The target environment is:

- Windows as the main desktop and IDE host
- WSL2 Ubuntu as the Linux-compatible shell
- Docker Desktop for PostgreSQL and future services
- Python with virtual environments
- Codex as the coding assistant
- a primary model API
- GitHub for version control and CI

## Recommended Setup Order

1. install Git and Python
2. enable WSL2 and install Ubuntu
3. install Docker Desktop
4. install your IDE and verify Codex access
5. configure your model API key
6. create the workspace directories
7. initialize the first project
8. run PostgreSQL in Docker
9. run a FastAPI hello world
10. test a minimal model API call
11. push the baseline project to GitHub

## Expected Baseline Project

Your first baseline should include:

- a FastAPI `/health` endpoint
- a minimal test
- Dockerized PostgreSQL
- `.env.example`
- README
- a basic model API client
