import json
import logging

import arcane
from arcane.engine import ArcaneEngine
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from github import Github

from studio.github import get_prs, get_user_repos, list_repos_by_owner
from studio.prompts import PR_DESCRIPTION

g = Github(settings.GITHUB_PAT)
logger = logging.getLogger(__name__)


def view_pull_requests(request, owner=None, repo=None):
    repos_by_owner = list_repos_by_owner()
    if not owner or not repo:
        prs = []
    else:
        prs = get_prs(f"{owner}/{repo}")
    return render(request, "index.html", {
        "repos": repos_by_owner,
        "prs": prs,
        "repo_owner": owner,
        "repo_name": repo,
        "selected_repo": f"{owner}/{repo}",
        "active_tab": "pull-request-manager",
    })


@require_POST
def generate_description(request, owner, repo):
    pr_number = request.POST.get('pr_number')
    engine = ArcaneEngine()
    prompt = PR_DESCRIPTION.format(pr_number=pr_number)
    try:
        task = engine.create_task(f"{owner}/{repo}", prompt)
    except arcane.exceptions.ApiException as e:
        logger.error(f"Failed to create task: {e}")
        msg = str(e)
        parsed_json = json.loads(e.body)
        if parsed_json.get('details'):
            msg = parsed_json.get('details')
        return render(request, "error.html", {
            "repos": list_repos_by_owner(),
            "error": msg
        })

    return redirect(reverse('view_task', args=(owner, repo, task.id,)))


