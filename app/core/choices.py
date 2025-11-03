from django.utils.translation import gettext_lazy as _

EVENT_TYPE_CHOICES = (
        ('traditional', _('Traditional')),
        ('festive', 'Festive'),
        ('ritual', 'Ritual')
    )

CHIEF_TYPE = (
        ('paramount', 'Paramount'),
        ('subchief', 'Sub Chief'),
        ('divisional', 'Divisional')
    )


DOCUMENT_TYPE = (
        ('article', 'Article'),
        ('conference_paper', 'Conference paper'),
        ('research_paper', 'Research paper'),
        ('book', 'Book'),
        ('chapter', 'Chapter'),
    )

SITE_TYPE = (
    ('cultural', 'Cultural'),
    ('natural', 'Natural'),
)

ARTIFACT_TYPE = (
    ('clothing', 'Clothing'),
    ('jewelry', 'Jewelry'),
    ('tool', 'Tool'),
    ('other', 'Other'),
)

STATUS_CHOICES = (
        ('draft', _('Pending Verification')),
        ('vetting', _('Vetting')),
        ('verified', _('Verified')),
        ('published', _('Published')),
    )
