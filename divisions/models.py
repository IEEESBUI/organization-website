from django.db import models

class Division(models.Model):
    id_name = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Activity(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='activities')
    description = models.CharField(max_length=255)
    
    def __str__(self):
        return self.description

class Project(models.Model):
    title = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='projects')
    description = models.TextField()
    image = models.ImageField(upload_to='divisions/images/', blank=True, null=True)
    
    def __str__(self):
        return self.title

class Leader(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='leaders')
    image = models.ImageField(upload_to='divisions/images/leaders/', blank=True, null=True)
    
    def __str__(self):
        return self.name 