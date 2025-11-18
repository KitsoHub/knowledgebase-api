1. ### Project Structure
| Syntax | Description |
| ----------- | ----------- |
| `docker-compose run --rm app sh -c "django-admin startproject app ."`  | Start project in the current directory |
| `docker-compose run --rm app sh -c "django-admin startapp core"`  | Start app |

### **Onboarding App**
- Used for creating, updating and viewing onboardings.

**Onboarding App structure**
- app/onboarding/tests/
- app/onboarding/urls
- app/onboarding/serializers
- app/onboarding/apps
- app/onboarding/views

### **Policies App**
- Used for creating, updating and viewing policies.

**Policy App structure**
- app/policies/tests/
- app/policies/urls
- app/policies/serializers
- app/policies/apps
- app/policies/views


### **Knowledge Base App**
- Used organizational information, including policies, compliance guidelines, and onboarding materials.

**Knowledge Basestructure**
- app/knowledgebase/tests/
- app/knowledgebase/urls
- app/knowledgebase/serializers
- app/knowledgebase/apps
- app/knowledgebase/views


**Sites App structure**
- app/sites/tests/
- app/sites/urls
- app/sites/serializers
- app/sites/apps
- app/sites/views



2. ### Set Up
| Syntax | Description |
| ----------- | ----------- |
| `docker build .`  | Build the image using the docker file |
| `docker-compose build`  | Build the image using docker compose configurations |
| `docker-compose run --rm app sh -c "python manage.py makemigrations "`| Make migrations |
| `docker-compose run --rm app sh -c "python3 manage.py createsuperuser" `  | Creating a super user eg (admin123) |
| `docker-compose up`  | Start all the services |



3. ### Apps Set Up
| Syntax | Description |
| ----------- | ----------- |
| `docker-compose run --rm app sh -c "python manage.py startapp sites "`| Create a sites app |


4. ### Migrations
| Syntax | Description |
| ----------- | ----------- |
| `docker-compose run --rm app sh -c "python manage.py makemigrations "`| Make migrations |
| `docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate "`| Migrate |


5. ### Tests
| Syntax | Description |
| ----------- | ----------- |
| `docker-compose run --rm app sh -c "python manage.py test core "`| All tests for models |
| `docker-compose run --rm app sh -c "python manage.py test --tag siteapis "`| All tests for siteapis |
| `docker-compose run --rm app sh -c "python manage.py test --tag verificationflow "`| All tests for verifications |

6. ### Container Access
| Syntax | Description |
| ----------- | ----------- |
| `docker exec -it knowledgebase-api_app_1 /bin/bash"`| Django Rest App Container |
| `docker exec -it knowledgebase-api_db_1 /bin/bash"`| Database Container |
