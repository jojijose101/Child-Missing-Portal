from django.db import models

# Create your models here.
from django.db import models

class MissingChild(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=200)

    image = models.ImageField(upload_to='children/')
    embedding = models.BinaryField()

    status = models.CharField(
        max_length=20,
        default='missing'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
