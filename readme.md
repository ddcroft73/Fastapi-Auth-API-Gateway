

## FastAPI Auth Gateway

A Python FastAPI service to authenticate authorize and manage my user base. As of now I am going forward with a small, small micro service architecture. I had initially planned to use a prebuilt project that had the boilerplate in place for dealing with the database, login, registration, password recovery, etc. I met with a lot of issues in this endeavor and decided to breakdown [Tiangolos'](https://github.com/tiangolo/full-stack-fastapi-postgresql/tree/master) Starter Project. It, and every other boilerplate project I tried had a lot of dependency issues(typical after 3 years) and I scrapped the idea, and decided to do it myself. However, I am leaning heavy on his code. It's going to save me a lot of time and the knowledge gained in the process is worth a lot to me. The way he handles the mundane tasks that all user based web apps must encounter has taught me a lot, and I don't have to alter much at all (There were actually a few errors. I'm really surprised they got through. They were rather trivial, which leads me to believe that others just fixed them and moved on.). Given my experience with this stuff (prior exp programming, very little with web dev.) I believe it would be prudent to start with a monolith (They say its easier). However I have already built the 
[email service](https://github.com/ddcroft73/email-service-v2/tree/main). (This one is all me and my code, and it's still under development.) I am rather happy with that part and thus far it's pretty strong and should fullfill my needs. It looks like I'm going to continue on the MSA path.

The API is now 100% functional. Database with users table. All CRUD operations work succesfully. Now to focus on tweaking the endpoints a bit. But for all intents and purposes, its a fully functioning Auth API Gateway that will create, edit, and delete users, with superuser priveledges as needed. Password recovery and reset. I still need to incorporate the API calls to the notification service for sending emails. The BP code for that is there.

## Warning: 
This application is desinged for a specific purpose and tailored to my needs. (It is at this point AUg 8,2023 basic enough anyone could probably use it) If anyone does find this. Use at your own risk. There is nothing malevolent about it but it's a custom job. So I should say good luck. It's so far having to be tweaked to run a bit differently between my Desktop WSL2 and my laptop Ubuntu 20.0.4. For some reason, they aren't exactly the same and it's working my nerves that I have to implement little differences between te two. Actually, this is probably due in fact to my ignorance and hopefully I will figure it all out.  

## Sandbox Testing: 
As of now I am spinning up a container beside that app in development to run sripts in to test and tweak the endpoints. It makes more sense than just writing a separate program in another directory on both computers. This way I can carry it from computer to computer. I do Intend to include some more tradtional tests as well. But For some reason Curl does not play well with this API. I get Invalid HTTP request and for some reason it will not effect changes to the user data. It has to be python scripts or... shit I hope JS requests work... Havent even gotten that far... ok, assuming they will. This shouldgive me an equally effective way to test the API.


## Tech Stack:
- FastAPI
- Alembic (migrations)
- SQLAlchemy
- PostgreSQL
- Celery Background tasks
- Celery Beat
- Docker-compose
- Custom Logging


## Users Attributes:
- Basic: 
  - id  - Set by the DB
  - email - Used as login and used as a link between Users DB and the Clock DB
  - password -  Two guesses
  - is_active
  - is_superuser
  - ful_name
- Additions:
  - phone_number - optional in case user would like to recieve check-ins via SMS
  - is_verified  - True when user verifies their Email
- Security additions:
  - admin_pin        - Admin only. Extra layer of security for admin.
  - failed_attempts  - How many tries to login.
  - lockout_time     - The amount of time to lock out a user.
  - account_locked   - True if the account is locked.

## Latest Changes:
- Added a Sandbox testing container. (see above)
- Removeed the revisions from the database and Started fresh. It felt ignorant to leave those backwards revisions and it would definitley cause trouble when trying to do a clean install.
- Due to an issue between my desktop and laptop, the `worker` service must be ran with `backend.dockerfile` on the desktop. (I'll deal with this later)
- Started writing sandbox script(s) for endpoint testing...

## Thoughts:
So at this point I need to be deciding how I intend to incorporate the core functionality of this app. My biggest question is DO I just go ahead and add it to this app? or do I make yet another service that does just that. That would give me:

- Notification Service Was Email, but Im thinking about incorporating the others as well.(Email, SMS, Social Media)
- Auth Gateway
- Main API that handles "WHat the app does"

That's only 3. Unless I should break the Notifications Service into 3? (Email, SMS, Social Media). hmmm Im trying to think about which modules would get the most action. As far as Notiications, Emails will be sent probably on the reg. And Maybe SMS depending on how the users config their preferences. Social Media will likely only be dispatched when A package deploys. That would be a busy service. Auth Gateway will be used to register, login (Only after the token has expired) The Main API will be keepig track of a LOT of data and handling intervals to see if its indeed time to deploy... What about a deploy service? meh.. not there yet. I think I will try to keep it at 2, or 3. Is It going to be more expensive to deploy a cluster in docker compose? Should I scratch this and go back to using virtual environments, and figure out how to deploy them seperately? That in itself just sounds expensive..

Work IS getting done. 