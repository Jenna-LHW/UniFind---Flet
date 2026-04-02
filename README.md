# UniFind Flet App
## Overview

**UniFind Flet App** is a desktop/mobile application built with **Flet** that connects to the **UniFind Lost & Found Management System** backend. It allows users to:

* Report lost or found items
* Search and filter items
* Manage their account via API authentication
* Interact with the system without using a browser

This app communicates with the backend via **RESTful API endpoints**.

## Features
* **User Authentication** – Login and register with your UniFind account
* **Lost Item Reporting** – Submit details about lost items
* **Found Item Reporting** – Submit details about found items
* **Search & Filter** – Browse items using search and filters
* **Responsive UI** – Works on desktop and mobile platforms

## Installation & Setup

### Clone the Repository

```bash
git clone https://github.com/Jenna-LHW/UniFind.git
cd unifind
```

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```
## Configuration
* Update the API base URL in your Flet app code to point to your Django backend, for example:

```
API_BASE_URL = "http://127.0.0.1:8000/api/
```
* Make sure your Django backend is running and accessible.
In the django project:

```
python manage.py runserver
```

## Running the App

Start the Flet app with:

```
python main.py
```

The app window will launch, allowing you to login, report items, and interact with the system.