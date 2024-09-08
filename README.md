# Distributed-Key-Value-Store-with-Fault-Tolerance
To read the README.md in Italian, click [here](README_ita.md)

## Index

1. [Overview](#1-overview)
   - [Project Structure](./myLib/Project_Structure.md)
2. [Enviroment setup](#2-enviroment-setup)
3. [Installation](#2-installation)
4. [Running the Application](#4-running-the-application)
5. [API Endpoints](#5-api-endpoints)


## **1. Overview**

This project implements a distributed key-value store with fault tolerance using replication. The system allows users to specify a replication factor and handles server failures and recoveries.
- ### Project Structure
Refer to the [project structure.md](design_document.md) for the system architecture, consistency model, and fault tolerance strategies.

## **2. Enviroment setup**
Before running the code, it's important to take some precautions and set up your environment properly. Follow these steps:
1. Create a Virtual Environment:
   - Open your terminal or command prompt.
   - Run the following command to create a virtual environment named "venv":` python -m venv venv`
2. Activate the Virtual Environment:
   - If you're using Windows:    `.\venv\Scripts\activate`
   - If you're using Unix or MacOS:    `source ./venv/Scripts/activate`
3. Deactivate the Environment (When Finished):
   - Use the following command to deactivate the virtual environment:    `deactivate`
4. Install Dependencies:
   - After cloning the project and activating the virtual environment, install the required dependencies using:    `pip install -r requirements.txt`
     This command downloads all the non-standard modules required by the application.
5. If your Python version used to generate the virtual environment doesn't contain an updated version of pip, update pip using:  `pip install --upgrade pip `

### Requirements

- Python
- Flask
- SQLite

## **3. Installation**

1. Clone the repository:
    ```sh
    git clone https://github.com/AlessiaRossi/Teleassistance-Supervised-Clustering.git
    cd Distributed-Key-Value-Store-with-Fault-Tolerance
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## **4. Running the Application**

1. Start the Flask application:
    ```sh
    python run.py
    ```

2. The application will be available at `http://127.0.0.1:5000`.

3. Use the command-line interface (CLI) to interact with the application:
    ```sh
    python client.py
    ```

4. Follow the on-screen options to perform various operations such as setting replication strategy, writing key-value pairs, reading values, deleting key-value pairs, failing nodes, recovering nodes, and demonstrating fail-recover behavior.

5. Run the test suite:
    ```sh
    python -m unittest discover -s tests
    ```

## **5. API Endpoints**

- `POST /write`: Write a key-value pair.
- `GET /read/<key>`: Read a value by key.
- `DELETE /delete/<key>`: Delete a key-value pair.
- `POST /fail/<int:node_id>`: Simulate a node failure.
- `POST /recover/<int:node_id>`: Recover a failed node.
- `GET /nodes`: Get the status of all nodes.


## Report

Refer to the [report.md](report.md) for experimental results and analysis.
