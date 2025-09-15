# Prepare a branch with auto-fix changes and a commit ready for PR
param(
  [string]$branchName = "auto/fix-baseline-and-format",
  [string]$commitMsg = "chore: apply auto-fixes and regenerate baseline (ci_head)"
)
Write-Output "Creating branch $branchName"
git checkout -b $branchName
Write-Output "Adding changed files"
git add ci_head/ tools/
Write-Output "Committing: $commitMsg"
git commit -m $commitMsg
Write-Output "Done. To push and open a PR:"
Write-Output "  git push --set-upstream origin $branchName"
Write-Output "Then open a PR on GitHub from $branchName -> release-v0.7.2"
