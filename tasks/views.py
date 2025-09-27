from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Team, Task
from django import forms
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

@login_required
def member_detail(request, user_id):
	# Only team lead can view
	profile = Profile.objects.get(user=request.user)
	if profile.role != 'lead':
		return redirect('dashboard')
	member = get_object_or_404(Profile, user__id=user_id, team=profile.team)
	tasks = Task.objects.filter(assigned_to=member.user)
	return render(request, 'member_detail.html', {
		'member': member,
		'tasks': tasks,
	})
def home(request):
	return render(request, 'home.html')
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Team, Task
from django import forms

class CustomSignupForm(UserCreationForm):
	ROLE_CHOICES = (
		('lead', 'Team Lead'),
		('member', 'Member'),
	)
	role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
	team = forms.CharField(required=False, help_text="Enter team name (for lead) or select/join existing team (for member)")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['team'].widget.attrs['list'] = 'team-list'

	def clean(self):
		cleaned_data = super().clean()
		role = cleaned_data.get('role')
		team_name = cleaned_data.get('team')
		if role == 'member' and not Team.objects.filter(name=team_name).exists():
			self.add_error('team', 'Team does not exist. Please enter a valid team name.')
		return cleaned_data
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

def signup(request):
	if request.method == 'POST':
		form = CustomSignupForm(request.POST)
		if form.is_valid():
			user = form.save()
			role = form.cleaned_data['role']
			team_name = form.cleaned_data['team']
			if role == 'lead':
				team, _ = Team.objects.get_or_create(name=team_name)
			else:
				team = Team.objects.filter(name=team_name).first()
			Profile.objects.create(user=user, role=role, team=team)
			login(request, user)
			return redirect('dashboard')
	else:
		form = CustomSignupForm()
	teams = Team.objects.all()
	return render(request, 'registration/signup.html', {'form': form, 'teams': teams})

from .models import Profile, Task, Team
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone

class TaskForm(forms.ModelForm):
	class Meta:
		model = Task
		fields = ['title', 'description', 'assigned_to', 'team']

@login_required
def dashboard(request):
	profile = Profile.objects.get(user=request.user)
	if profile.role == 'lead':
		return team_lead_dashboard(request, profile)
	else:
		return member_dashboard(request, profile)

@login_required
def team_lead_dashboard(request, profile):
	team = profile.team
	members = Profile.objects.filter(team=team)
	# Prepare cards for each member (including self)
	member_cards = []
	for member in members:
		member_tasks = Task.objects.filter(assigned_to=member.user)
		card_summary = {
			'total': member_tasks.count(),
			'completed': member_tasks.filter(status='completed').count(),
			'pending': member_tasks.filter(status='pending').count(),
		}
		member_cards.append({
			'profile': member,
			'summary': card_summary,
		})
	# Date range filter for lead's own tasks
	start_date = request.GET.get('start_date')
	end_date = request.GET.get('end_date')
	lead_tasks = Task.objects.filter(assigned_to=request.user)
	if start_date and end_date:
		lead_tasks = lead_tasks.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
	lead_summary = {
		'total': lead_tasks.count(),
		'completed': lead_tasks.filter(status='completed').count(),
		'pending': lead_tasks.filter(status='pending').count(),
	}
	# Heatmap for lead's own tasks
	from collections import Counter
	completed_per_day = Counter()
	for t in lead_tasks.filter(status='completed'):
		if t.completed_at:
			day = t.completed_at.date()
			completed_per_day[day] += 1
	import datetime
	today = datetime.date.today()
	days = [today - datetime.timedelta(days=i) for i in range(29, -1, -1)]
	heatmap = []
	max_count = max(completed_per_day.values()) if completed_per_day else 1
	color_map = ['#eee', '#b6f5b6', '#6ee96e', '#2dc82d', '#158c15']
	for day in days:
		count = completed_per_day.get(day, 0)
		intensity = int((count / max_count) * 4) if max_count else 0
		color = color_map[intensity]
		heatmap.append({'date': day, 'count': count, 'color': color})
	# Assign task form (lead can assign to anyone, including self)
	if request.method == 'POST':
		form = TaskForm(request.POST)
		if form.is_valid():
			task = form.save(commit=False)
			task.assigned_by = request.user
			task.status = 'pending'
			task.save()
			return redirect('dashboard')
	else:
		form = TaskForm()
		form.fields['assigned_to'].queryset = User.objects.filter(profile__team=team)
		form.fields['team'].queryset = Team.objects.filter(id=team.id)
	return render(request, 'team_lead_dashboard.html', {
		'member_cards': member_cards,
		'form': form,
		'lead_summary': lead_summary,
		'heatmap': heatmap,
		'start_date': start_date,
		'end_date': end_date,
	})

def member_dashboard(request, profile):
		user = request.user
		# Add new task
		if request.method == 'POST' and 'add_task' in request.POST:
			title = request.POST.get('title')
			description = request.POST.get('description')
			if title:
				Task.objects.create(
					title=title,
					description=description,
					assigned_to=user,
					assigned_by=user,
					team=profile.team,
					status='pending'
				)
			return redirect('dashboard')
		# Mark task as completed
		if request.method == 'POST' and 'complete' in request.POST:
			task_id = request.POST.get('complete')
			try:
				task = Task.objects.get(id=task_id, assigned_to=user, status='pending')
				task.status = 'completed'
				from django.utils import timezone
				task.completed_at = timezone.now()
				task.save()
			except Task.DoesNotExist:
				pass
			return redirect('dashboard')
		# Date range filter
		start_date = request.GET.get('start_date')
		end_date = request.GET.get('end_date')
		tasks = Task.objects.filter(assigned_to=user)
		if start_date and end_date:
			tasks = tasks.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
		pending_tasks = tasks.filter(status='pending')
		completed_tasks = tasks.filter(status='completed')
		summary = {
			'total': tasks.count(),
			'completed': completed_tasks.count(),
			'pending': pending_tasks.count(),
		}
		# Calendar heatmap data: count completed tasks per day
		from collections import Counter
		completed_per_day = Counter()
		for t in completed_tasks:
			if t.completed_at:
				day = t.completed_at.date()
				completed_per_day[day] += 1
		# Prepare last 30 days for heatmap
		import datetime
		today = datetime.date.today()
		days = [today - datetime.timedelta(days=i) for i in range(29, -1, -1)]
		heatmap = []
		max_count = max(completed_per_day.values()) if completed_per_day else 1
		color_map = ['#eee', '#b6f5b6', '#6ee96e', '#2dc82d', '#158c15']
		for day in days:
			count = completed_per_day.get(day, 0)
			intensity = int((count / max_count) * 4) if max_count else 0
			color = color_map[intensity]
			heatmap.append({'date': day, 'count': count, 'color': color})
		return render(request, 'dashboard.html', {
			'pending_tasks': pending_tasks,
			'completed_tasks': completed_tasks,
			'heatmap': heatmap,
			'start_date': start_date,
			'end_date': end_date,
			'summary': summary,
		})
