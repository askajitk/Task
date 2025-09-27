from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
	name = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

class Profile(models.Model):
	ROLE_CHOICES = (
		('lead', 'Team Lead'),
		('member', 'Member'),
	)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
	role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')

	def __str__(self):
		return f"{self.user.username} ({self.role})"

class Task(models.Model):
	STATUS_CHOICES = (
		('pending', 'Pending'),
		('completed', 'Completed'),
	)
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	assigned_to = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE)
	assigned_by = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.CASCADE)
	team = models.ForeignKey(Team, on_delete=models.CASCADE)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	completed_at = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return self.title
