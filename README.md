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

![image](https://github.com/dluc/github-stats/assets/371009/66a07b5c-6271-4515-b753-1a1f4614db32)
![image](https://github.com/dluc/github-stats/assets/371009/eb94b7b1-8762-43aa-a691-320738e6906b)
![image](https://github.com/dluc/github-stats/assets/371009/15ce1c3a-7772-4755-ae1e-d732938acc19)
![image](https://github.com/dluc/github-stats/assets/371009/6a91ef59-5fa5-4ee8-8060-4533a8ca0d9d)
![image](https://github.com/dluc/github-stats/assets/371009/952a9f6c-db31-41c5-82c1-b53436a465be)


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
