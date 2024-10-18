# Cinema Event Management API

This project is a simple Cinema Event Management API developed using Django. It was created by Ahmed Alnahhal, a beginner in Python programming, as a stepping stone to develop a comprehensive cinema application using Flutter. The API showcases my ability to handle RESTful API implementations.

## Overview

The Cinema Event Management API provides endpoints for managing movie events, including creating, updating, and retrieving information about films. One of the key features of this API is that accessing movie data does not require authentication, making it user-friendly and accessible. However, actions such as creating films, managing guests, and handling reservations require authentication.

## Key Features

- **RESTful API**: The application follows RESTful principles, allowing for easy integration and interaction with other applications.
- **No Authentication for Movie Retrieval**: Users can access movie data without needing to authenticate.
- **Authentication Required for Certain Actions**: Creating films, managing guests, and handling reservations require user authentication.
- **Deployment**: The API is hosted on Vercel, ensuring high availability and scalability.
- **Database Management**: The database is hosted on Aiven, providing a reliable backend for storing movie information.

## Application Structure

This API is designed to work alongside two other applications:

1. **Desktop Event Management Application (`desktop_events_app`)**: This application will provide full control over the API, allowing users to manage movie events effectively.
2. **Mobile Event Application (`event_mobile_app`)**: This mobile application will provide users with access to movie information and event management on their smartphones.

## Getting Started

### Prerequisites

- Python 3.x
- Django
- Django REST Framework

### Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd cinema_event_management_api
