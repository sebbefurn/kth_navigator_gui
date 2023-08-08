from django.db import models

class User(models.Model):
    course = models.CharField(max_length=100, null=True)
    grade = models.IntegerField(null=True)

class TextBlock(models.Model):
    text = models.CharField(max_length=1000)
    is_user = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-created_at']
