# Text Analysis Web Application

This project is a simple web-based application that allows users to input text manually and analyze the provided content. It is lightweight, easy to set up, and runs on a Docker container for portability and ease of deployment.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask for serving the web app)
- **Containerization**: Docker

## Requirements

- **Docker**: Installed on your system
- **Port**: The application runs on port `8000` by default
- **Modern Browser**: A modern web browser to interact with the app

## Installation and Setup

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone <repository-url>
cd <project-folder>
```

### 2. Dockerized Setup

#### Build the Docker Image

To build the Docker image for the application, use the following command:

```bash
docker build -t my-app .
```

#### Run the Docker Container

Once the image is built, run the container:

```bash
docker run -p 8000:8000 my-app
```

#### Access the Application

After the container is running, open your web browser and go to:

```
http://127.0.0.1:8000
```
