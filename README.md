Any user can create events. When creating an event, the user can specify the emails of invited users. Only the owner can delete or modify a created event.

All users have access to view all events. A user can filter events by specifying whether they are invited using invited="true" (to see events they are invited to) or invited="false" (to see events they are not invited to). If "invited" is not specified, both invited and non-invited events will be displayed. Events can also be filtered by name and date.

Users can register for an event through api/events/register/.
The registration endpoint is api/register, and the authentication endpoint is api/token.

Swagger documentation is available at api/docs/swagger/.

SQLite is used as the database for this application.

### How to run:
Build and run the container:

```docker build -t events_manager .```

```docker run -p 8000:8000 events_manager```

Apply migrations:

```docker exec <container_id> python3 manage.py makemigrations```

```docker exec <container_id> python3 manage.py migrate```
