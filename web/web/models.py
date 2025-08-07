from django.db import models


class Comment(models.Model):
    user = models.CharField(max_length=50)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    def __str__(self):
        return f'{self.user}: {self.text[:30]}'

    class Meta:
        ordering = ['created_at']



class Users(models.Model):
    user = models.CharField(max_length=50, default='Гость')
    site = models.CharField(max_length=255, default='-')
    email = models.CharField(max_length=255, default='-')

    def __str__(self):
        return self.user