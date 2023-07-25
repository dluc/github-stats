A set of scripts to quickly and periodically generate a web page with statistics
about your GitHub repository pull requests.

* PR summary
* PRs open more than 5 days, last 4 months
* Avg time to close a PR, last 4 months
* Avg time a PR stays open, last 4 months
* PRs open and closed, last 4 months
* % PR closed in <5 days | <10 days | <15 days, last 4 months
* Internal and External PRs %, last 4 months
* External PRs open for more than 10 days
* Internal PRs open for more than 10 days
* PRs without assignees

![image](https://github.com/dluc/github-stats/assets/371009/2d6802ac-fa8c-4c07-889f-0e765e6d40b2)
![image](https://github.com/dluc/github-stats/assets/371009/44179a2e-dad0-48ed-844d-e8b7ef79b593)
![image](https://github.com/dluc/github-stats/assets/371009/0ef2d6e2-d9d5-42a1-afdf-a52c27ae9c54)
![image](https://github.com/dluc/github-stats/assets/371009/fc00492a-f659-47a2-8078-dd853359c403)
![image](https://github.com/dluc/github-stats/assets/371009/5c2b957c-1a56-4234-a61d-694186a1370f)

# Setup

1. Install GitHub CLI (gh)
1. Copy `.env.example` to `.env` and set your GitHub token and Gist URL
2. Copy `config.py.example` to `config.py` and set the list of TEAM_MEMBERS
3. Setup your target repo: `git clone https://github.com/<YOUR REPO>.git repo`
4. Setup `run.sh` in your crontab, to run every 20 mins (or less frequently)

# Test run

Run `run.sh`

# How does it work?

The scripts download GitHub Pull Requests stats using GitHub CLI, saving the information
locally in two files (`prs.json` and `prs.csv`). The data in these files is used to
generate a few stats about your repo pull requests, writing the results to a GitHub
gist markdown file. 

The page contains some graphs built with `quickchart.io`. You can see the rendered
stats creating a web page like this:

```html
<html>

<body>
    <div style="width:1100px;margin:20px auto;">
        <script src="https://gist.github.com/<...user...>/<...gist id...>.js"></script>
    </div>
</body>

</html>
```

# Troubleshooting

* Use a Linux shell, e.g. Ubuntu bash or WSL
* Install Python 3.8.10+
* Make sure `gh` is visible to your crontab user.
* Scripts work with `main` branch, change `config.py` otherwise.
* The GitHub token needs write access to update a gist.
