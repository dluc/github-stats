# Author: Devis Lucato, https://github.com/dluc

from config import MAIN_BRANCH, CSV_FILE, JSON_FILE, FIELDS, TEAM_MEMBERS
import json, os, csv, datetime, math
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import urllib.parse


# Create CSV file if missing
def create_csv():
    # Create CSV file if missing
    if not os.path.isfile(CSV_FILE):
        with open(CSV_FILE, "w", newline="\n") as data_file:
            writer = csv.DictWriter(data_file, fieldnames=FIELDS, dialect="unix", quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()


# Read CSV file and return PRs as a dict, sorted by PR number
def read_csv():
    with open(CSV_FILE, "r", newline="\n") as data_file:
        reader = csv.DictReader(data_file, fieldnames=FIELDS, dialect="unix", quoting=csv.QUOTE_MINIMAL)
        data = list(reader)
        # Remove header
        if len(data) > 0:
            data.pop(0)

    # Organize by PR number
    new_data = dict()
    for row in data:
        key = f"{row['number']}".zfill(8)
        new_data[key] = row

    # Sort by PR number
    data = dict(sorted(new_data.items()))

    return data


# Update the CSV file using the new data from the JSON file
def update_csv():
    create_csv()
    data = read_csv()

    # Read JSON data
    with open(JSON_FILE) as input_file:
        prs = json.load(input_file)

    # Update CSV data with new PRs
    for pr in prs:
        key = f"{pr['number']}".zfill(8)

        # List of assignees
        assignees = ""
        for assignee in pr["assignees"]:
            assignees += assignee["login"] + ","
        if assignees != "":
            assignees = assignees[:-1]

        # List of labels
        labels = ""
        for label in pr["labels"]:
            labels += label["name"] + ","
        if labels != "":
            labels = labels[:-1]

        data[key] = {
            "number": pr["number"],
            "state": pr["state"],
            "closed": pr["closed"],
            "isDraft": pr["isDraft"],
            "title": pr["title"],
            "branch": pr["baseRefName"],
            "createdAt": pr["createdAt"],
            "updatedAt": pr["updatedAt"],
            "mergedAt": pr["mergedAt"],
            "closedAt": pr["closedAt"],
            "author": pr["author"]["login"],
            "assignees": assignees,
            "labels": labels,
            "url": pr["url"],
        }

    # Sort CSV data by key
    data = dict(sorted(data.items()))

    # Write CSV data
    with open(CSV_FILE, "w", newline="\n") as data_file:
        writer = csv.DictWriter(data_file, fieldnames=FIELDS, dialect="unix", quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for new_data_row in data.values():
            writer.writerow(new_data_row)


# Check if PR is from an external contributor
def is_external_pr(pr):
    if pr["author"] in TEAM_MEMBERS:
        return False
    else:
        return True


# Get the date the PR was closed or merged (or Now if still open)
def get_pr_end_date(pr, current=datetime.datetime.now(datetime.timezone.utc)):
    if pr["state"] == "MERGED":
        return parse(pr["mergedAt"])
    if pr["state"] == "CLOSED":
        return parse(pr["closedAt"])
    return current


# Calculate how many days the PR has been open
def calc_open_time(pr):
    begin = parse(pr["createdAt"])
    end = get_pr_end_date(pr)
    return int((end - begin).total_seconds())


# Calculate stats for a given date range
# Date format: YYYY-MM-DDTHH:MM:SSZ, e.g. e.g. 2023-02-27T21:35:12Z
def calc_pr_stats(date_from, date_to):
    one_day = 3600 * 24

    result = lambda: None
    result.int_count = 0
    result.ext_count = 0
    result.int_closed_count = 0
    result.ext_closed_count = 0
    result.int_open_by_days = dict()
    result.ext_open_by_days = dict()
    result.int_avg_open_days = 0
    result.ext_avg_open_days = 0
    result.int_avg_days_to_close = 0
    result.ext_avg_days_to_close = 0

    prs = read_csv()
    types = [True, False]
    for external in types:
        pr_count = 0
        closed_count = 0
        total_open_days = 0
        total_days_to_close = 0
        avg_open_days = 0
        avg_days_to_close = 0

        open_count_by_days = dict()
        open_count_by_days["5-"] = 0
        open_count_by_days["5+"] = 0
        open_count_by_days["10-"] = 0
        open_count_by_days["10+"] = 0
        open_count_by_days["15-"] = 0
        open_count_by_days["15+"] = 0
        open_count_by_days["20+"] = 0
        open_count_by_days["30+"] = 0

        for pr in prs.items():
            pr = pr[1]

            if external != is_external_pr(pr):
                continue

            # Ignore drafts, PRs on branches other than main
            if pr["branch"] != MAIN_BRANCH or pr["isDraft"] == "TRUE":
                continue

            begin_period = parse(date_from)
            end_period = parse(date_to)
            pr_begin = parse(pr["createdAt"])
            pr_end = get_pr_end_date(pr, end_period)

            # Skip PRs outside the selected period
            if pr_end < begin_period or pr_begin > end_period:
                continue

            pr_count += 1

            # Calculate how many days the PR has been open
            if pr_end < end_period:
                days_open = math.ceil((pr_end - pr_begin).total_seconds() / one_day)
            else:
                days_open = math.ceil((end_period - pr_begin).total_seconds() / one_day)
            total_open_days += days_open

            # Calculate how many days it took to close the PR
            if (pr["state"] == "MERGED" or pr["state"] == "CLOSED") and pr_end <= end_period:
                total_days_to_close += days_open
                closed_count += 1

            # Averages
            if pr_count > 0:
                avg_open_days = total_open_days / pr_count
            if closed_count > 0:
                avg_days_to_close = total_days_to_close / closed_count

            # Counter by days open
            if days_open >= 30:
                open_count_by_days["5+"] += 1
                open_count_by_days["10+"] += 1
                open_count_by_days["15+"] += 1
                open_count_by_days["20+"] += 1
                open_count_by_days["30+"] += 1
            elif days_open >= 20:
                open_count_by_days["5+"] += 1
                open_count_by_days["10+"] += 1
                open_count_by_days["15+"] += 1
                open_count_by_days["20+"] += 1
            elif days_open >= 15:
                open_count_by_days["5+"] += 1
                open_count_by_days["10+"] += 1
                open_count_by_days["15+"] += 1
            elif days_open >= 10:
                open_count_by_days["5+"] += 1
                open_count_by_days["10+"] += 1
                open_count_by_days["15-"] += 1
            elif days_open >= 5:
                open_count_by_days["5+"] += 1
                open_count_by_days["15-"] += 1
                open_count_by_days["10-"] += 1
            else:
                open_count_by_days["15-"] += 1
                open_count_by_days["10-"] += 1
                open_count_by_days["5-"] += 1

        # Save data for external and internal PRs
        if external:
            result.ext_open_by_days = open_count_by_days
            result.ext_count = pr_count
            result.ext_closed_count = closed_count
            result.ext_avg_open_days = avg_open_days
            result.ext_avg_days_to_close = avg_days_to_close
        else:
            result.int_open_by_days = open_count_by_days
            result.int_count = pr_count
            result.int_closed_count = closed_count
            result.int_avg_open_days = avg_open_days
            result.int_avg_days_to_close = avg_days_to_close

    return result


# Calculate PR stats
def print_stats2(weeks=4, with_header=True):
    now = datetime.datetime.now(datetime.timezone.utc)
    n_weeks_ago = now - relativedelta(weeks=weeks)

    s = calc_pr_stats(n_weeks_ago.strftime("%Y-%m-%dT%H:%M:%SZ"), now.strftime("%Y-%m-%dT%H:%M:%SZ"))

    print(f"## Last {weeks} weeks")

    if with_header:
        print("PR  | Internal | External")
        print("--- | -------- | --------")
        print(f"Open              | {s.int_count}| {s.ext_count}")
        print(f"Closed            | {s.int_closed_count} | {s.ext_closed_count}")
        print(f"Avg days to close | {s.int_avg_days_to_close:.1f} | {s.ext_avg_days_to_close:.1f}")
        print(f"Avg days open     | {s.int_avg_open_days:.1f} | {s.ext_avg_open_days:.1f}")
    else:
        print("Internal | External")
        print("-------- | --------")
        print(f"{s.int_count} | {s.ext_count}")
        print(f"{s.int_closed_count} | {s.ext_closed_count}")
        print(f"{s.int_avg_days_to_close:.1f} | {s.ext_avg_days_to_close:.1f}")
        print(f"{s.int_avg_open_days:.1f} | {s.ext_avg_open_days:.1f}")

    def c2s(count, total):
        return f"{count} ({count/total*100:.1f}%)"

    if with_header:
        print(
            f"open <5 days  | {c2s(s.int_open_by_days['5-'], s.int_count)} | {c2s(s.ext_open_by_days['5-'], s.ext_count)}"
        )
        print(
            f"open >5 days  | {c2s(s.int_open_by_days['5+'], s.int_count)} | {c2s(s.ext_open_by_days['5+'], s.ext_count)}"
        )
        print(
            f"open >10 days | {c2s(s.int_open_by_days['10+'], s.int_count)} | {c2s(s.ext_open_by_days['10+'], s.ext_count)}"
        )
        print(
            f"open >20 days | {c2s(s.int_open_by_days['20+'], s.int_count)} | {c2s(s.ext_open_by_days['20+'], s.ext_count)}"
        )
        print(
            f"open >30 days | {c2s(s.int_open_by_days['30+'], s.int_count)} | {c2s(s.ext_open_by_days['30+'], s.ext_count)}"
        )
    else:
        print(f"{c2s(s.int_open_by_days['5-'], s.int_count)}  | {c2s(s.ext_open_by_days['5-'], s.ext_count)}")
        print(f"{c2s(s.int_open_by_days['5+'], s.int_count)}  | {c2s(s.ext_open_by_days['5+'], s.ext_count)}")
        print(f"{c2s(s.int_open_by_days['10+'], s.int_count)} | {c2s(s.ext_open_by_days['10+'], s.ext_count)}")
        print(f"{c2s(s.int_open_by_days['20+'], s.int_count)} | {c2s(s.ext_open_by_days['20+'], s.ext_count)}")
        print(f"{c2s(s.int_open_by_days['30+'], s.int_count)} | {c2s(s.ext_open_by_days['30+'], s.ext_count)}")


def calc_draw_stats():
    now = datetime.datetime.now(datetime.timezone.utc)
    stats = lambda: None
    stats.period = dict()
    for i in range(0, 120, 7):
        date_from = now - relativedelta(days=(i + 7))
        date_to = now - relativedelta(days=i)
        key = f"{date_from.strftime('%Y-%m-%dT%H:%M:%SZ')}|{date_to.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        stats.period[key] = calc_pr_stats(
            date_from.strftime("%Y-%m-%dT%H:%M:%SZ"), date_to.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
    return stats


def draw_avg_to_close_stats(data):
    print("## Avg time to close a PR, last 4 months\n")
    print("Stats about the PRs that have been merged or closed.\n")
    labels = []
    values1 = []
    for key in data.period.keys():
        stats = data.period[key]
        parts = key.split("|")
        label = parts[1].split("T")[0]
        labels.insert(0, label)

        value = (stats.int_avg_days_to_close + stats.ext_avg_days_to_close) / 2
        values1.insert(0, f"{value:.2f}")

    graph = (
        "{type:'line',data:{labels:['"
        + "','".join(labels)
        + "'],datasets:[{label:'days',data:["
        + ",".join(values1)
        + "],lineTension:0.2,fill:true,borderColor:'#003366',backgroundColor:'#FFCC00'}]}}"
    )
    print(f"![stats](https://quickchart.io/chart?c={urllib.parse.quote(graph)})")


def draw_avg_open_stats(data):
    print("## Avg time a PR stays open, last 4 months\n")
    print("Stats about all the PRs, merged, closed and still open.\n")
    labels = []
    values1 = []
    for key in data.period.keys():
        stats = data.period[key]
        parts = key.split("|")
        label = parts[1].split("T")[0]
        labels.insert(0, label)

        value = (stats.int_avg_open_days + stats.ext_avg_open_days) / 2
        values1.insert(0, f"{value:.2f}")

    graph = (
        "{type:'line',data:{labels:['"
        + "','".join(labels)
        + "'],datasets:[{label:'days',data:["
        + ",".join(values1)
        + "],lineTension:0.2,fill:true,borderColor:'#003366',backgroundColor:'#FFCC00'}]}}"
    )
    print(f"![stats](https://quickchart.io/chart?c={urllib.parse.quote(graph)})")


def draw_prs_out_of_sla(data):
    print("## PRs open more than 5 days, last 4 months\n")
    labels = []
    values1 = []
    for key in data.period.keys():
        stats = data.period[key]
        parts = key.split("|")
        label = parts[1].split("T")[0]
        labels.insert(0, label)

        value = stats.int_open_by_days["5+"] + stats.ext_open_by_days["5+"]
        values1.insert(0, f"{value:.2f}")

    graph = (
        "{type:'line',data:{labels:['"
        + "','".join(labels)
        + "'],datasets:["
        + "{label:'open PRs',data:["
        + (",".join(values1))
        + "],lineTension:0.2,fill:true,borderColor:'#003366',backgroundColor:'#FFCC00'}"
        + "]}}"
    )
    print(f"![stats](https://quickchart.io/chart?c={urllib.parse.quote(graph)})")


def draw_int_ext_stats(data):
    print("## Internal and External PRs %, last 4 months\n")
    labels = []
    values1 = []
    values2 = []
    for key in data.period.keys():
        stats = data.period[key]
        parts = key.split("|")
        label = parts[1].split("T")[0]
        labels.insert(0, label)

        total = stats.int_count + stats.ext_count
        if total > 0:
            values1.insert(0, f"{stats.int_count/total*100:.1f}")
            values2.insert(0, f"{stats.ext_count/total*100:.1f}")
        else:
            values1.insert(0, f"0")
            values2.insert(0, f"0")

    graph = (
        "{type:'line',data:{labels:['"
        + "','".join(labels)
        + "'],datasets:["
        + "{label:'% internal',data:["
        + (",".join(values1))
        + "],lineTension:0.4,fill:false,borderColor:'#00539CFF',backgroundColor:'#00539CFF'},"
        + "{label:'% external',data:["
        + (",".join(values2))
        + "],lineTension:0.4,fill:false,borderColor:'#97BC62FF',backgroundColor:'#97BC62FF'},"
        + "]}}"
    )
    print(f"![stats](https://quickchart.io/chart?c={urllib.parse.quote(graph)})")


def draw_open_close_stats(data):
    print("## PRs open and closed, last 4 months\n")
    labels = []
    values1 = []
    values2 = []
    for key in data.period.keys():
        stats = data.period[key]
        parts = key.split("|")
        label = parts[1].split("T")[0]
        labels.insert(0, label)

        values1.insert(0, f"{stats.int_count + stats.ext_count}")
        values2.insert(0, f"{stats.int_closed_count + stats.ext_closed_count}")

    graph = (
        "{type:'line',data:{labels:['"
        + "','".join(labels)
        + "'],datasets:["
        + "{label:'open',data:["
        + (",".join(values1))
        + "],lineTension:0.2,fill:true,borderColor:'#FDD20EFF',backgroundColor:'#FDD20E99'},"
        + "{label:'merged+closed',data:["
        + (",".join(values2))
        + "],lineTension:0.2,fill:true,borderColor:'#006400',backgroundColor:'#32CD32'},"
        + "]}}"
    )
    print(f"![stats](https://quickchart.io/chart?c={urllib.parse.quote(graph)})")

    labels = []
    values1 = []
    values2 = []
    total_open = 0
    total_closed = 0
    for key in data.period.keys():
        stats = data.period[key]
        parts = key.split("|")
        label = parts[1].split("T")[0]
        labels.insert(0, label)

        total_open = total_open + stats.int_count + stats.ext_count
        total_closed = total_closed + stats.int_closed_count + stats.ext_closed_count
        values1.append(f"{total_open}")
        values2.append(f"{total_closed}")

    graph = (
        "{type:'line',data:{labels:['"
        + "','".join(labels)
        + "'],datasets:["
        + "{label:'open',data:["
        + (",".join(values1))
        + "],lineTension:0.2,fill:true,borderColor:'#FDD20EFF',backgroundColor:'#FDD20E99'},"
        + "{label:'merged+closed',data:["
        + (",".join(values2))
        + "],lineTension:0.2,fill:true,borderColor:'#006400',backgroundColor:'#32CD32'},"
        + "]}}"
    )
    print(f"![stats](https://quickchart.io/chart?c={urllib.parse.quote(graph)})")


def draw_close_percentage_stats(data):
    print("## % PR closed in <5 days | <10 days | <15 days, last 4 months\n")
    labels = []
    values1 = []
    values2 = []
    values3 = []
    for key in data.period.keys():
        stats = data.period[key]
        parts = key.split("|")
        label = parts[1].split("T")[0]
        labels.insert(0, label)

        lt_5days = stats.int_open_by_days["5-"] + stats.ext_open_by_days["5-"]
        lt_10days = stats.int_open_by_days["10-"] + stats.ext_open_by_days["10-"]
        lt_15days = stats.int_open_by_days["15-"] + stats.ext_open_by_days["15-"]
        total = stats.int_count + stats.ext_count
        if total > 0:
            values1.insert(0, f"{lt_5days/total*100:.1f}")
            values2.insert(0, f"{lt_10days/total*100:.1f}")
            values3.insert(0, f"{lt_15days/total*100:.1f}")
        else:
            values1.insert(0, f"0")
            values2.insert(0, f"0")
            values3.insert(0, f"0")

    graph = (
        "{type:'line',data:{labels:['"
        + "','".join(labels)
        + "'],datasets:["
        + "{label:'<5 days',data:["
        + (",".join(values1))
        + "],pointRadius:1,borderWidth:2,lineTension:0,fill:true,borderColor:'#4CAF50FF',backgroundColor:'#77DD77FF'},"
        + "{label:'<10 days',data:["
        + (",".join(values2))
        + "],pointRadius:1,borderWidth:2,lineTension:0,fill:true,borderColor:'#99CC99FF',backgroundColor:'#CCFFCCFF'},"
        + "{label:'<15 days',data:["
        + (",".join(values3))
        + "],pointRadius:1,borderWidth:2,lineTension:0,fill:true,borderColor:'#999999FF',backgroundColor:'#CCCCCC99'},"
        + "]}}"
    )
    print(f"![stats](https://quickchart.io/chart?c={urllib.parse.quote(graph)})")


# Show PRs out of 5, sorted by oldest first
def print_slow_prs(days=10, external=True):
    now = datetime.datetime.now(datetime.timezone.utc)
    n_days_ago = now - relativedelta(days=days)
    one_day = 3600 * 24
    prs = read_csv()

    title = f"\n## Internal PRs open for more than {days} days\n"
    if external:
        title = f"\n## External PRs open for more than {days} days\n"

    for pr in prs.items():
        pr = pr[1]

        # Ignore drafts, PRs on branches other than main, PRs not open
        if (
            pr["branch"] != MAIN_BRANCH
            or pr["isDraft"] == "TRUE"
            or pr["state"] != "OPEN"
            or external != is_external_pr(pr)
        ):
            continue

        created_at = parse(pr["createdAt"])

        # Ignore PRs created less than n weeks ago
        if created_at > n_days_ago:
            continue

        # Print title if first PR
        if title:
            print(title)
            title = None

        # Print PR details: title, url, days open
        days_open = math.ceil(calc_open_time(pr) / one_day)
        print(f"* [{days_open} days] #{pr['number']} - {pr['author']} - [{pr['title']}]({pr['url']})")


# Show PRs without assignees
def prs_without_assignees():
    prs = read_csv()
    title = f"## PRs without assignees\n"
    for pr in prs.items():
        pr = pr[1]

        # Ignore drafts, PRs on branches other than main, PRs not open
        if pr["branch"] != MAIN_BRANCH or pr["isDraft"] == "TRUE" or pr["state"] != "OPEN":
            continue

        if pr["assignees"] != "":
            continue

        # Print title if first PR
        if title:
            print(title)
            title = None

        print(f"* #{pr['number']} - {pr['author']} - [{pr['title']}]({pr['url']})")


def gen_report():
    print("# Semantic Kernel PR stats\n")

    now = datetime.datetime.now(datetime.timezone.utc)
    print("Last update: " + now.strftime("%Y-%m-%d %H:%M:%S %Z") + "\n")

    print("## PR summary\n")
    print("<table><tr><td>\n")
    print_stats2(weeks=2, with_header=True)
    print("\n</td><td>\n")
    print_stats2(weeks=4, with_header=False)
    print("\n</td><td>\n")
    print_stats2(weeks=8, with_header=False)
    print("\n</td></tr></table>\n")

    stats = calc_draw_stats()

    # How many PRs are open more than 5 days
    draw_prs_out_of_sla(stats)

    # How long does it take to close a PR
    draw_avg_to_close_stats(stats)

    # How long do PRs stay open
    draw_avg_open_stats(stats)

    # How many PRs are closed and how many are open
    draw_open_close_stats(stats)

    # % of PRs closed in <5 days | <10 days | <15 days
    draw_close_percentage_stats(stats)

    # Internal vs External %
    draw_int_ext_stats(stats)

    print_slow_prs(days=10, external=True)
    print_slow_prs(days=10, external=False)
    print("\n")

    prs_without_assignees()
    print("\n")
