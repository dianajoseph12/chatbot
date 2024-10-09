
# Chatbot

This project is a chatbot system built using Django and integrated with Redis for efficient data storage and retrieval. The system allows for dynamic interaction with a chatbot, displays user-specific chat histories, and stores file uploads. The chatbot is also capable of fetching and displaying leave information based on an admin's input in the database. 

# Key Features
## Django Backend:
The core of the application is built using Django, handling authentication, file uploads, and database management.

## Chroma Integeration
The vector embeddings of documents are stored in chroma. For each document there exist individual collections.

## Redis Integration:
Redis is used as a secondary database for storing chat histories and session data.
Redis keys are generated using UUID for each user, providing efficient lookup and management of chat history.

## Employee Login: 
Employees can log in to access the chatbot interface, check leave status, and view chat history.

## Admin Login: 
Admins can log in to update holiday/leave information and view employee-specific chat histories.

## File Upload System:
File uploads are handled by Django, and each file is assigned a unique collection name based on a UUID.

## Chatbot
Both employees and admin can chat with the uploaded document. 

## Chat History Display:
Redis stores chat histories using UUIDs generated for each user.
Use the redis_manager.py file to interact with Redis, storing and retrieving chat data as needed.



# Setup Instructions
## Prerequisites
Python 3.12, 
Chroma (vector database)
Redis (for chat history storage), 
SQLite/Other Database (default database for Django models)

# Installation
## 1. Clone the repository:
git clone https://github.com/dianajoseph12/chatbot.git

## 2. Navigate to your project directory
cd demo

## 3. Install required dependencies:
pip install -r requirements.txt

## 4.Set up your Redis instance and ensure it's running locally or on your desired environment.

## 5. Apply Django migrations:
python manage.py migrate

## 6. Run the Django development server:
python manage.py runserver





