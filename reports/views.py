import logging

from arcane.engine import ArcaneEngine
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from demo.github import list_repos_by_owner
from demo.prompts import GENERATE_REPORT
from .models import Report

logger = logging.getLogger(__name__)


def view_reports(request, owner, repo):
    reports = Report.objects.all()
    return render(request, "list_reports.html", {
        "reports": reports,
        "repos": list_repos_by_owner(),
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "active_tab": "reports",
    })


@require_POST
def generate_report(request, owner, repo):
    prompt = request.POST.get('prompt')
    title = request.POST.get('title')  # Get the title from the form
    engine = ArcaneEngine()
    task = engine.create_task(f"{owner}/{repo}", GENERATE_REPORT.format(report_description=prompt))
    report = Report.objects.create(prompt=prompt, task_id=task.id, title=title)  # Save the title
    return redirect(reverse('view_report', args=(owner, repo, report.id,)))


def view_report(request, owner, repo, report_id):
    report = Report.objects.get(id=report_id)
    engine = ArcaneEngine()
    task = engine.get_task(report.task_id)
    if task.status == "completed":
        report.result = task.result
        report.save()
        return render(request, "view_report.html", {
            "report": report,
            "repos": list_repos_by_owner(),
            "task": task,
            "repo_owner": owner,
            "repo_name": repo,
            "selected_repo": f"{owner}/{repo}",
            "active_tab": "reports",
        })
    else:
        return render(request, "view_task.html", {
            "repos": list_repos_by_owner(),
            "task": task,
            "repo_owner": owner,
            "repo_name": repo,
            "selected_repo": task.github_project,
            "active_tab": "tasks",
        })
