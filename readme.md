

## FastAPI Backend

A Python FastAPI service to authenticate authhorize and manage a user base. As of now I am going forward with a small, small micro service architecture. I had initially planned to use a prebuilt project that had the boilerplate in place for dealing with the database, login, registration. I met with a lot of issues in this endeavor and decided to breakdown [Tiangolo](https://github.com/tiangolo/full-stack-fastapi-postgresql/tree/master) Starter Project. It, and every other boilerplate project I tried had a lot of dependency issues(typical after 3 years) and I scrapped the idea to do it myself. However, I am leaning heavy on his code. Its going to save me a lot of time and the knowledge gained is worth a lot to me. The way he handles the mundane tasks that all user based web apps must encoubter has taught me a lot, and I dodnt have to alter much at all. Given my experience with this stuff (prior exp programming, very little with web dev.)I believe it would be prudent to start with a monolith (They say its easier). However I have already built the 
[email service](https://github.com/ddcroft73/email-service-v2/tree/main). (This one is all me and my code.) I am rather happy with that part and thus far it's pretty strong and should fullfill my needs. It looks like Im going to continue on the MSA path.

API is now 100% functional. Database with users table. All CRUD operations work succesfully. Now to focus on tweaking the endpoints a bit. But for all intents and purposes, its a fully functioning Auth API Gateway that will create, edit, and delete users, with superuser priveledges as needed. Password recovery and reset. I need to incorporate the API calls to the notification service for sending New user, password rrecovery and other emails.


## Tech Stack:
- FastAPI
- Alembic (migrations)
- SQLAlchemy
- PostgreSQL
- Celery Background tasks
- Celery Beat
- Docker-compose
- Custom Logging

So at this point I need to be deciding how I intend to incorporate the core functionality of this app. My biggest question is DO I just go ahead and add it to this app? or do I make yet another service that does just that. That would give me:

- Notification Service Was Email, but Im thinking about incorporating the others as well.(Email, SMS, Social Media)
- Auth Gateway
- Main API that handles "WHat the app does"

That's only 3. Unless I should break the Notifications Service into 3? (Email, SMS, Social Media). hmmm Im trying to think about which modules would get the most action. As far as Notiications, Emails will be sent probably on the reg. And Maybe SMS depending on how the users config their preferences. Social Media will likely only be dispatched when A package deploys. That would be a busy service. Auth Gateway will be used to register, login (Only after the token has expired) The Main API will be keepig track of a LOT of data and handling intervals to see if its indeed time to deploy... What about a deploy service? meh.. not there yet. I think I will try to keep it at 2, or 3. Is It going to be more expensive to deploy a cluster in docker compose? Should I scratch this and go back to using virtual environments, and figure out how to deploy them seperately? That in itself just sounds expensive..

Work IS getting done. 