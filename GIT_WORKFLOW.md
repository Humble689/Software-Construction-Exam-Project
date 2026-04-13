# CineQuest - Git Workflow & Standards

## Table of Contents
1. [Branching Strategy](#branching-strategy)
2. [Commit Message Conventions](#commit-message-conventions)
3. [Branch Naming Conventions](#branch-naming-conventions)
4. [Pull Request Process](#pull-request-process)
5. [Code Review Guidelines](#code-review-guidelines)
6. [Merging & Conflict Resolution](#merging--conflict-resolution)
7. [Common Git Commands](#common-git-commands)

---

## Branching Strategy

We use a modified Git Flow model with clear separation between branches:

### Main Branches

#### `main` Branch
- **Purpose:** Production-ready code only
- **Protection:** Requires PR review and passing CI/CD
- **Merge Source:** Only from `dev` branch via release PR
- **Tagging:** Each merge to main gets a version tag (v1.0.0, v1.0.1, etc.)
- **Access:** Team lead approval required

```
Restrictions:
- No direct commits allowed
- Requires at least 2 approvals
- CI/CD pipeline must pass
- Automated tests must be green
```

#### `dev` Branch
- **Purpose:** Integration branch for features
- **Protection:** Requires PR review and passing tests
- **Merge Source:** Feature branches and bugfix branches
- **Merge Target:** Feature branches should merge from dev (pull latest)
- **Frequency:** Updated multiple times per week

```
Workflow:
1. Create feature branch from dev
2. Push commits to feature branch
3. Open PR against dev
4. After approval, merge to dev
5. Delete feature branch after merge
```

### Supporting Branches

#### Feature Branches (`feature/*`)
- **Naming:** `feature/<team-member-name>`
  - Example: `feature/moses-api-setup`
  - Example: `feature/joel-nextjs-layout`

- **Created From:** `dev` branch
- **Merged Back To:** `dev` branch
- **Deletion:** Delete after merge is complete

**Lifetime:** Weeks (long-running features)
**Scope:** Single feature or user story

#### Bugfix Branches (`bugfix/*`)
- **Naming:** `bugfix/<issue-number>-<description>`
  - Example: `bugfix/42-cors-header-crash`
  - Example: `bugfix/128-movie-search-timeout`

- **Created From:** `dev` branch
- **Merged Back To:** `dev` branch
- **Deletion:** Delete after merge is complete

**Lifetime:** Days to weeks
**Scope:** Single bug fix

#### Documentation Branches (`docs/*`)
- **Naming:** `docs/<document-name>`
  - Example: `docs/api-endpoints`
  - Example: `docs/setup-guide`

- **Created From:** `main` or `dev` depending on urgency
- **Merged Back To:** Target branch
- **Deletion:** Delete after merge is complete

**Lifetime:** Days
**Scope:** Documentation updates only

---

## Commit Message Conventions

We follow **Conventional Commits** specification for clear, semantic commit messages.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New feature or functionality | `feat: add user authentication with JWT` |
| `fix` | Bug fix | `fix: resolve null pointer in movie search` |
| `refactor` | Code refactoring without feature changes | `refactor: extract API logic to service layer` |
| `test` | Adding or updating tests | `test: add MovieCard unit tests` |
| `docs` | Documentation updates | `docs: add API endpoint documentation` |
| `chore` | Maintenance, dependency updates | `chore: update Django to 4.2.1` |
| `style` | Formatting, missing semicolons (no logic change) | `style: format code with black formatter` |
| `perf` | Performance improvements | `perf: optimize N+1 queries in movie list` |

### Scope Guidelines

Scope should be the component, module, or area affected:

**Backend Examples:**
- `models` - Django models
- `api` - REST API views/serializers
- `auth` - Authentication system
- `search` - Search functionality
- `cache` - Caching system
- `tests` - Test infrastructure

**Frontend Examples:**
- `components` - React components
- `hooks` - Custom React hooks
- `types` - TypeScript definitions
- `api` - API client/integration
- `styles` - Styling and CSS
- `tests` - Test files

### Subject Line Rules

- Use imperative mood: "add feature" not "added feature"
- Don't capitalize first letter: "add" not "Add"
- No period (.) at the end
- Limit to 50 characters maximum
- Be specific and descriptive

### Body Section (Optional but Recommended)

Use when the change needs explanation:

```
fix(api): resolve CORS blocking frontend requests

CORS middleware was positioned after CommonMiddleware, causing
all preflight requests to be rejected. Moved CorsMiddleware
before CommonMiddleware in MIDDLEWARE setting.

This resolves issues where POST requests from Next.js frontend
were being blocked by browser CORS policy.
```

### Footer Section (Optional)

Use for linking to issues:

```
fix(auth): resolve JWT token expiration bug

Fixed issue where refresh tokens were not being validated.

Fixes #156
Closes #159
```

### Commit Examples

**Good Examples:**
```
feat(models): add MovieRating model with user relationships
fix(api): correct pagination offset calculation
refactor(components): extract Header into separate file
test(backend): add authentication permission tests
docs: write API documentation with examples
chore: update dependencies to latest versions
```

**Bad Examples:**
```
fixed stuff
Updated code
WIP
misc changes
final version
```

---

## Branch Naming Conventions

### Standard Format
```
<type>/<descriptor>
```

### Examples by Type

**Feature Branches:**
- `feature/moses-backend-setup`
- `feature/joel-nextjs-layout`
- `feature/alvin-typescript-strict`

**Bugfix Branches:**
- `bugfix/42-cors-header-issue`
- `bugfix/cors-middleware-order`

**Documentation Branches:**
- `docs/api-documentation`
- `docs/setup-guide`

**Hotfix Branches:**
- `hotfix/critical-security-patch`

### Rules

- Use lowercase only
- Use hyphens to separate words (not underscores)
- Keep names concise but descriptive
- Include team member name in feature branches for accountability
- Include issue number for bugfix branches when available
- Maximum 50 characters recommended

---

## Pull Request Process

### 1. Before Creating a PR

```bash
# Ensure your branch is up to date with dev
git checkout dev
git pull origin dev

# Switch back to your feature branch
git checkout feature/your-feature

# Rebase on latest dev (recommended over merge)
git rebase dev

# If conflicts occur, resolve them
git add <resolved-files>
git rebase --continue

# Force push to update remote branch
git push origin feature/your-feature --force-with-lease
```

### 2. Opening a Pull Request

Use the PR template (create `.github/pull_request_template.md`):

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update

## Related Issue
Fixes #123 (replace with actual issue number)

## How to Test
1. Steps to reproduce behavior
2. Expected behavior
3. Actual behavior before fix

## Testing Checklist
- [ ] Unit tests written/updated
- [ ] All tests passing locally
- [ ] Manual testing completed
- [ ] No console errors/warnings

## Code Quality Checklist
- [ ] Code follows project style guidelines
- [ ] No new warnings generated
- [ ] Comments added for complex logic
- [ ] Documentation updated if needed

## Screenshots (if applicable)
Add screenshots for UI changes

## Reviewers
@team-member-1 @team-member-2
```

### 3. PR Naming Convention

```
[AREA] Brief description of change
```

Examples:
- `[Backend] Add JWT authentication system`
- `[Frontend] Fix responsive mobile menu`
- `[Docs] Update API documentation`
- `[Tests] Add MovieCard component tests`

### 4. PR Workflow

1. **Create PR** from your feature branch to `dev`
2. **Wait for CI/CD** to pass (tests, linting, builds)
3. **Request reviewers** (minimum 2 reviewers)
4. **Address feedback** with new commits (don't force push after review started)
5. **Get approval** from reviewers
6. **Squash and merge** to dev (keep commit history clean)
7. **Delete branch** after merge

---

## Code Review Guidelines

### For Reviewers

#### What to Check

1. **Code Quality**
   - Does code follow project style?
   - Are variable names clear and descriptive?
   - Is the code DRY (Don't Repeat Yourself)?
   - Are there any obvious bugs or logic errors?

2. **Architecture**
   - Does this fit the project architecture?
   - Are design patterns used correctly?
   - Is the solution scalable?

3. **Testing**
   - Are tests included?
   - Do tests cover important cases?
   - Are edge cases handled?

4. **Documentation**
   - Are complex sections documented?
   - Are function signatures clear?
   - Is API documentation updated?

5. **Performance**
   - Are there N+1 query problems?
   - Could this cause memory leaks?
   - Are database queries optimized?

#### Review Process

```
1. Read the PR description and understand intent
2. Review commits one by one
3. Run tests locally if significant changes
4. Leave constructive feedback
5. Approve once ready for merge
```

#### Approval Conditions

Approve when:
- Code follows conventions
- Tests are adequate
- No security concerns
- Documentation is complete
- Functionality is correct

Request changes when:
- Critical bugs found
- Security issues present
- Tests fail or missing
- Architecture concerns exist
- Code quality below standard

### For Authors

#### Responding to Feedback

```
✅ Do:
- Acknowledge feedback positively
- Explain reasoning if disagreeing
- Make requested changes promptly
- Thank reviewers for thorough review

❌ Don't:
- Dismiss feedback without consideration
- Argue about style preferences
- Make unrelated changes
- Force push without explanation
```

---

## Merging & Conflict Resolution

### Merge Strategy

#### Recommended: Squash and Merge
```bash
# Squash feature commits into one clean commit
# Use for: Feature branches (keeps main history clean)
git checkout dev
git pull origin dev
git merge --squash feature/your-feature
git commit -m "feat: add new feature"
git push origin dev
```

**Benefits:**
- Clean, linear commit history on main
- Easy to revert entire feature if needed
- Easier to understand project history

#### Alternative: Rebase and Merge
```bash
# Rebase feature commits on top of dev
# Use for: Bugfix branches (maintains commit history)
git checkout feature/your-feature
git rebase dev
git checkout dev
git merge --ff-only feature/your-feature
git push origin dev
```

### Resolving Conflicts

#### Step 1: Identify Conflicts
```bash
git status
# Shows files with conflicts (both modified)
```

#### Step 2: View Conflict Markers
```
<<<<<<< HEAD
your changes
=======
incoming changes
>>>>>>>
```

#### Step 3: Resolve Conflicts

Edit files to resolve conflicts:

```bash
# Option A: Keep your changes
git checkout --ours <file>

# Option B: Keep incoming changes
git checkout --theirs <file>

# Option C: Manually edit and combine changes
# (recommended for important files)
vi <file>
```

#### Step 4: Complete Resolution
```bash
# Mark files as resolved
git add <resolved-files>

# Complete rebase
git rebase --continue

# Or abort if something went wrong
git rebase --abort
```

#### Conflict Prevention

```bash
# Keep feature branch updated with dev regularly
git fetch origin
git rebase origin/dev

# Communicate with team about overlapping changes
# Review other PRs before starting your own
```

### Deleting Branches

After merging:

```bash
# Delete local branch
git branch -d feature/your-feature

# Delete remote branch
git push origin --delete feature/your-feature

# Or delete in GitHub UI when PR is merged
```

---

## Common Git Commands

### Setting Up

```bash
# Clone repository
git clone https://github.com/cinequest/cinequest.git
cd cinequest

# Configure user (if first time)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Creating & Switching Branches

```bash
# Create new feature branch from dev
git checkout dev
git pull origin dev
git checkout -b feature/my-feature

# Or in one command (Git 2.23+)
git switch -c feature/my-feature
```

### Making Changes

```bash
# See what changed
git status
git diff

# Stage specific files
git add src/components/MovieCard.tsx
git add tests/

# Stage everything
git add .

# Commit with message
git commit -m "feat(components): add MovieCard with rating display"

# Amend last commit (if not pushed yet)
git commit --amend --no-edit
```

### Updating Your Branch

```bash
# Fetch latest changes from remote
git fetch origin

# Rebase on dev (recommended)
git rebase origin/dev

# Or merge dev if rebase causes issues
git merge origin/dev

# If rebase has conflicts
git rebase --abort
git merge origin/dev
```

### Pushing & Creating PR

```bash
# Push feature branch
git push origin feature/my-feature

# Push with tracking (first time)
git push -u origin feature/my-feature

# Force push after rebase (safe version)
git push origin feature/my-feature --force-with-lease
```

### Viewing History

```bash
# See commits
git log
git log --oneline
git log --graph --oneline --all

# See changes in specific file
git log -- src/components/MovieCard.tsx
git diff main feature/my-feature -- src/components/
```

### Undoing Changes

```bash
# Discard local changes (be careful!)
git checkout -- src/components/MovieCard.tsx

# Unstage file
git reset HEAD src/components/MovieCard.tsx

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Revert a commit (creates new commit)
git revert abc123
```

---

## Team Best Practices

### Daily Workflow

1. **Start of day:** Pull latest changes
   ```bash
   git checkout dev
   git pull origin dev
   ```

2. **Creating feature:** Create feature branch
   ```bash
   git checkout -b feature/your-name-feature
   ```

3. **During work:** Commit frequently with clear messages
   ```bash
   git commit -m "feat(scope): clear description"
   ```

4. **End of day:** Push to remote for backup
   ```bash
   git push origin feature/your-name-feature
   ```

5. **Before PR:** Update with latest dev
   ```bash
   git rebase origin/dev
   ```

### Communication

- **Large refactors:** Discuss with team first
- **Breaking changes:** Announce in team channel
- **Conflicts:** Reach out to related author
- **Blocked:** Ask for help in pull request comments

### Code Review Standards

- Aim for 24-48 hour review turnaround
- Be constructive and respectful
- Approve promptly once concerns addressed
- Thank reviewers for their time

---

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow Cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)

---

**Last Updated:** April 2026
**Document Version:** 1.0
**Maintained By:** NKANGI Moses (Team Lead)
