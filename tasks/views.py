import markdown
from arcane.engine import ArcaneEngine
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from repositories.views import render_with_repositories


@login_required
def view_task(request, owner, repo, task_id):
    task = ArcaneEngine().get_task(task_id)
    task.result = markdown.markdown(task.result)
    task.user_request = markdown.markdown(task.user_request)
    return render_with_repositories(request, "view_task.html", {
        "task": task,
        "selected_repo": task.github_project,
        "active_tab": "tasks",
    }, owner, repo)


@login_required
def list_tasks(request, owner, repo):
    tasks = [t for t in ArcaneEngine().list_tasks() if t.github_project == f"{owner}/{repo}"]

    return render_with_repositories(request, "list_tasks.html", {
        "tasks": tasks,
        "active_tab": "tasks",
    }, owner, repo)


@login_required
@require_POST
def create_task(request, owner, repo):
    if request.method == "POST":
        task_description = request.POST.get("task_description")
        if not task_description:
            raise ValueError("Task description is required.")
        else:
            try:
                task = ArcaneEngine().create_task(f"{owner}/{repo}", task_description)
            except Exception as e:
                msg = str(e)
                if e.data and e.data.error:
                    msg = e.data.error
                return render(request, "error.html", {
                    "error": f"Failed to create task: {msg}",
                })
            return redirect('view_task', owner=owner, repo=repo, task_id=task.id)
