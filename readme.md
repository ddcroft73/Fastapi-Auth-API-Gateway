

## FastAPI Auth Gateway

A Python FastAPI service to authenticate authorize and manage my user base. As of now I am going forward with a small, small micro service architecture. I had initially planned to use a prebuilt project that had the boilerplate in place for dealing with the database, login, registration, password recovery, etc. I met with a lot of issues in this endeavor and decided to breakdown [Tiangolos'](https://github.com/tiangolo/full-stack-fastapi-postgresql/tree/master) Starter Project. It, and every other boilerplate project I tried had a lot of dependency issues(typical after 3 years) and I scrapped the idea, and decided to do it myself. However, I am leaning heavy on his code. It's going to save me a lot of time and the knowledge gained in the process is worth a lot to me. The way he handles the mundane tasks that all user based web apps must encounter has taught me a lot, and I don't have to alter much at all (There were actually a few errors. I'm really surprised they got through. They were rather trivial, which leads me to believe that others just fixed them and moved on.). Given my experience with this stuff (prior exp programming, very little with web dev.) At first I thought it would be prudent to start with a monolith (They say its easier). However I have already built the [email service](https://github.com/ddcroft73/email-service-v2/tree/main). (This one is all me and my code, and it's still under development.) I am rather happy with that part and thus far it's pretty strong and should fullfill my needs. It looks like I'm going to continue on the MSA path.

This is a personal project and as it is, is a WIP. 

## Tech Stack:
- FastAPI
- Alembic (migrations)
- SQLAlchemy
- PostgreSQL
- Celery for Background tasks
- Docker-compose
- Custom Logging (Soon to 86 this for something a bit more robust. Mine is great for debugging, but I dont want to rely on it in production.)


## Micro Services: Auth Gateway

- Notification Service Was Email, but Im adding SMS as well... makes sense.
- Social API. An API that will make posts on the users behalf. This will be it's own service.
- Auth Gateway (This) This Service also stores the users basic and account data. 
- Main API that handles "WHat the app does" Clock API


## Latest Changes: 

#### 11/04/23
- Updated fasAPI to 0.104.0
- I moved the .env file to auth-server.env  
- Added env_file to the docker-compose file.
- Added fields to the database for 2FA. still need to code it.
- Added some new fields to the user and account tables to implement 2FA
- Removed failed_login_attempts.
- Found a fix for the `update bug`
- Added Delete by ID
- Added error checking for non existent records.
#### 11/12/23
- Added 2FA support
- Added Async support to frequent used endpoints, and all io functions.
- Revised some endpoint names
#### 11/20/23
- Updated the status code on HTTPExceptions for easier use by client
- Update Token schema
- Updated My logging Tool...


### TODO:

- Add the logic for Admin PIN Access (verify_admin_token), almost done
- Figure out a production logging setup. Working.
- Finish resend-verification.
- Finish Create User Admin
- Rate limiting, 
- Add logic for revoking Tokens. This will be based on the user logging out,
- 
  