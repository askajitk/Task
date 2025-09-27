# Team Task Management Django App

A web application for team task assignment and management. Team leads can assign tasks to members, view dashboards, summaries, and heatmaps. Members can view and complete tasks, add their own, and see progress.

## Features
- User authentication (signup, login, logout)
- Team lead/member roles
- Team dashboard for leads: member cards, task summary, heatmap
- Member dashboard: personal tasks, completion, heatmap
- Assign tasks to members (lead), self-task addition (member)
- Date range selection for summaries
- Responsive Bootstrap UI
- Live password suitability check
- Calendar heatmap with month/date labels

## Getting Started

### Prerequisites
- Python 3.12+
- Django 5.2.6

### Setup
1. Clone the repository:
   ```sh
git clone https://github.com/yourusername/teamtasks.git
cd teamtasks
```
2. Create and activate a virtual environment:
   ```sh
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```
3. Install dependencies:
   ```sh
pip install django
```
4. Run migrations:
   ```sh
python manage.py makemigrations
python manage.py migrate
```
5. Start the development server:
   ```sh
python manage.py runserver
```

## Usage
- Visit `http://127.0.0.1:8000/` in your browser.
- Sign up as a team lead or member.
- Team leads can assign tasks, view member dashboards, and summaries.
- Members can view, complete, and add tasks.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT
