

## FastAPI Backend

I'm not 100 on how this is going to play out. I am building a rather large app (As far as I'm concerned, anyway), and my first intention was to go with 
a micro service architecture. Given my experience with this stuff I believe it would be prudent to start with a monolith. However I have already built the 
[email service](https://github.com/ddcroft73/email-service-v2/tree/main). I am rather happy with that part and thus far it's pretty strong and should
fullfill my needs. I was going to use a fastAPI boilerplate template, but I must have tried out 8 of them to no avail. Dependency issues were rampant and
honestly none of them were exactly what I wanted. Yeh, I know You add what you want. Take away what you don't. Let's be honest. I enjoy this, so I'm going to 
build my own. Between what I know, The FastAPI docs, and what I've noticed on the other projects this should be a piece of cake(Famous last words). So Aside from the email service
I believe this will house the rest of the code to run the project. What to call it... lol. idek. I'm goint to start it out as nothing more than the Auth portion
for users to register, login, password recovery, etc. Once I get that done. I'll see where I am.

## Tech Stack:
- FastAPI
- Alembic (migrations)
- PostgresSQL
- Celery Background tasks
- Celery Beat
- Docker-compose
- TBD

As for now this readme is going to serve as my scratch pad. I'm going to hash it all out here as I do it. So here are my goals:
- Build the project structure... DONE
  - I'll be using the same setup as I did with my email service. That is using containers and docker compose.
- Build a basic fastapi app with endpoints intact,  but none functional... DONE
- Add celery for tasks (Beat will come later)... WORKING

