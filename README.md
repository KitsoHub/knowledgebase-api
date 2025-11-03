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


2. ### Set Up
| Syntax | Description |
| ----------- | ----------- |
| `docker build .`  | Build the image using the docker file |
| `docker-compose build`  | Build the image using docker compose configurations |
| `docker-compose run --rm app sh -c "python3 manage.py createsuperuser" `  | Creating a super user eg (admin123) |
| `docker-compose up`  | Start all the services |
