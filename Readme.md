# Project Title

Create an API for social networking application using Django Rest Framework with
below functionalities

## Description

The Social Networking Application is a platform designed to facilitate social interactions between users. It provides features such as user authentication, friend requests, and user profiles. Users can sign up for an account, log in securely, and search for other users to connect with. They can send friend requests to establish connections and manage their list of friends.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
  - [User Authentication](#user-authentication)
  - [Friend Requests](#friend-requests)

## Installation

### Using Docker

1. Clone the repository: `git clone https://github.com/your_username/your_project.git`
2. Navigate to the project directory: `cd your_project`
3. Build the Docker image: `docker-compose build`
4. Start the Docker containers: `docker-compose up`
5. The application should now be running and accessible at `http://localhost:8000`

## Usage

Explain how to use your project once it's installed. Include any configuration steps or environment setup required.

## API Documentation

### User Authentication

#### User Signup

- **Create User**: Endpoint to register a new user.
  - Method: POST
  - URL: `/signup/`
  - Request Body:
    ```json
    {
        "email": "user@example.com",
        "password": "your_password",
        "confirm_password": "your_password"
    }
    ```
  - Response: JSON object indicating success or failure.

#### User Login

- **User Login**: Endpoint to authenticate a user using basic authentication.
  - Method: POST
  - URL: `/login/`
  - Authentication: Basic authentication (username and password)
  - Response: JSON object indicating success or failure.

### Friend Requests

#### Create Friend Request

- **Send Friend Request**: Endpoint to send a friend request to another user.
  - Method: POST
  - URL: `/friend-requests/`
  - Request Body:
    ```json
    {
        "to_user": "friend@example.com"
    }
    ```
  - Authentication: Basic authentication required.
  - Response: JSON object indicating success or failure.

#### Accept Friend Request

- **Accept Friend Request**: Endpoint to accept a pending friend request.
  - Method: POST
  - URL: `/friend-requests/{request_id}/accept/`
  - Authentication: Basic authentication required.
  - Response: JSON object indicating success or failure.

#### Reject Friend Request

- **Reject Friend Request**: Endpoint to reject a pending friend request.
  - Method: POST
  - URL: `/friend-requests/{request_id}/reject/`
  - Authentication: Basic authentication required.
  - Response: JSON object indicating success or failure.

#### List Pending Requests

- **List Pending Requests**: Endpoint to retrieve a list of pending friend requests.
  - Method: GET
  - URL: `/friend-requests/list-pending-requests/`
  - Authentication: Basic authentication required.
  - Response: JSON array containing pending friend requests.
