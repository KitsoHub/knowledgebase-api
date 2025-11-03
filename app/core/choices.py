from django.utils.translation import gettext_lazy as _

DOCUMENT_TYPE = (
        ('article', 'Article'),
        ('conference_paper', 'Conference paper'),
        ('research_paper', 'Research paper'),
        ('book', 'Book'),
        ('chapter', 'Chapter'),
    )


ONBOARDING_TYPE = (
    ('operations', 'Operational'),
    ('leave', 'Leave taking'),
    ('training', 'Training'),
    ('other', 'Other'),
)

STATUS_CHOICES = (
        ('draft', _('Pending Verification')),
        ('vetting', _('Vetting')),
        ('verified', _('Verified')),
        ('published', _('Published')),
    )

KNOWLEDGE_CATEGORY = (
    ('onboarding', _('Onboarding')),
    ('policy', _('Policy')),
    ('procedure', _('Procedure')),
    ('compliance', _('Compliance')),
    ('general', _('General')))
