

### Working with Groups, Permissions

`python`
from django.contrib.auth.models import Group, Permission
for p in Permission.objects.all():
    print(p.pk, p.codename, pk.name)
- Django upon each model migration creates the safemethod permissions ( can add, delete, change, view)


--Shell plus
- python3 manage.py shell_plus --ipython

### Error handling
The use of transaction.atomic() ensures that any database changes are rolled back if an exception occurs, maintaining data integrity.
[transactions](https://docs.djangoproject.com/en/5.1/topics/db/transactions/)
[transactions 2](https://www.geeksforgeeks.org/transaction-atomic-with-django/)

### Testing
[testingConfig](https://www.django-rest-framework.org/api-guide/testing/#configuration)
[testing2](https://docs.djangoproject.com/en/5.1/topics/testing/tools/#the-test-client)
https://books.agiliq.com/projects/django-api-polls-tutorial/en/latest/testing-and-ci.html


## Next
- ensure the group permissions are granted
- check to see on the admin side and front end the filtering for different groups eg vetters, verifiers, publishers
- set published and display on the front end those that has publish status
- test comments from vetter to contributor-owner
- test workflow from vetter back to draft
- test workflow from verifier - vetter
- test workflow from publisher - verifier
- figure out how to enforce that the publisher group can only update the is_published field on the model
- check to see that the different groups can list data according to their roles

