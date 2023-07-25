#!/usr/bin/env bash
# Author: Devis Lucato, https://github.com/dluc

set -e

PATH="$PATH:/snap/bin/"

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/"

source .env

cd repo

gh pr list --state all --limit 2500 \
--json id,number,state,assignees,author,baseRefName,closed,closedAt,createdAt,headRefName,headRepository,headRepositoryOwner,isCrossRepository,isDraft,maintainerCanModify,mergeStateStatus,mergeable,mergedAt,mergedBy,updatedAt,url,title,labels \
> ../prs.json
