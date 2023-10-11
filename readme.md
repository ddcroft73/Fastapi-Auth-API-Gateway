

## FastAPI Auth Gateway

A Python FastAPI service to authenticate authorize and manage my user base. As of now I am going forward with a small, small micro service architecture. I had initially planned to use a prebuilt project that had the boilerplate in place for dealing with the database, login, registration, password recovery, etc. I met with a lot of issues in this endeavor and decided to breakdown [Tiangolos'](https://github.com/tiangolo/full-stack-fastapi-postgresql/tree/master) Starter Project. It, and every other boilerplate project I tried had a lot of dependency issues(typical after 3 years) and I scrapped the idea, and decided to do it myself. However, I am leaning heavy on his code. It's going to save me a lot of time and the knowledge gained in the process is worth a lot to me. The way he handles the mundane tasks that all user based web apps must encounter has taught me a lot, and I don't have to alter much at all (There were actually a few errors. I'm really surprised they got through. They were rather trivial, which leads me to believe that others just fixed them and moved on.). Given my experience with this stuff (prior exp programming, very little with web dev.) I believe it would be prudent to start with a monolith (They say its easier). However I have already built the 
[email service](https://github.com/ddcroft73/email-service-v2/tree/main). (This one is all me and my code, and it's still under development.) I am rather happy with that part and thus far it's pretty strong and should fullfill my needs. It looks like I'm going to continue on the MSA path.

The API is now 100% functional. meh... not quite, I need to fix some of the crud operations since I added the account table. Nothing major. Database with users table. Most CRUD operations work succesfully. Now to focus on tweaking the endpoints a bit. But for all intents and purposes, its a fully functioning Auth API Gateway that will create, edit, and delete users, with superuser priveledges as needed. Password recovery and reset. THe Email Verify portions works well. Contacts the email service, email service does its job. Need to incorporate SMS ....

I NEED TO JUST MAKE A FUCKING LIST....

<br>
Time is not on my side. Still have to make a living.

## Warning: 
This application is desinged for a specific purpose and tailored to my needs. If anyone does find this. Use at your own risk. There is nothing malevolent about it but it's a custom job. So I should say good luck. It works on my computer!

## Tech Stack:
- FastAPI
- Alembic (migrations)
- SQLAlchemy
- PostgreSQL
- Celery Background tasks
- Celery Beat Coming...
- Docker-compose
- Custom Logging (Soon to *6 this for something a bit more robust. Mine is great for debugging, but I dont want to rely on it in production.)


## Latest Changes:
- Removed Sandbox testing.. Plann to add tests I do..
- Removed the revisions from the database and Started fresh. It felt ignorant to leave those backwards revisions and it would definitley cause trouble when trying to do a clean install.
- Due to an issue between my desktop and laptop, the `worker` service must be ran with `backend.dockerfile` on the desktop. (I'll deal with this later)

Just moving along.. got the Account Table set up and working. Saves, updates, but still need to finis update user_id. 

## TODO
Need to finish endpoints and add the logic for Admin PIN Access.
Finish up User routes, 
Figure out a productionn logging setup.
A lot more Ill dive into when i have the time.

<hr>

### Initial Thoughts- (Old THoughts now)

So at this point I need to be deciding how I intend to incorporate the core functionality of this app. My biggest question is DO I just go ahead and add it to this app? or do I make yet another service that does just that. That would give me:

### Micro Services 
- Notification Service Was Email, but Im adding SMS as well... makes sense.
- Social API. An API that will make posts on the users behalf. This will be it's own service.
- Auth Gateway (This) This Service also stores the users basic and account data. 
- Main API that handles "WHat the app does" Clock API

