# MonetDbe-Python contribution policy

MonetDbe-Python is an open-source project; everyone is welcome and encouraged to help improve the quality of the product. You can help by reporting issues or even better fix issues yourself. We use GitHub as a central communication and development platform. Problems can be reported there. If you have a patch for MonetDbe-Python, we use the GitHub pull request system. Also to keep the MonetDbe-Python code quality high we have written down some guidelines for contributing, see below.

## General considerations

 * If you have problems or questions with/about git or GitHub, first check [1].
 * If you modify any code, make sure the test suite still runs (`pytest`).
   If it fails, fix the code or the relevant test.
 * The tested code coverage line count should increase, not decrease.

## Contribution procedure

 1. Create a GitHub account and set up SSH keys.
 2. Fork the MonetDbe-Python repository on GitHub [3].
 3. Create a branch and commit your changes to this branch.
 4. Push your branch to your GitHub fork (not the original MonetDbe-Python, you probably don't have permission).
 5. Issue a pull request [4].
 6. When the pull request is reviewed, and there are no problems, it will be accepted. Merging a pull request should always happen by someone else.
 7. It can happen there are some mistakes here and there; we use the GitHub commenting system to discuss these issues.
 8. If there is a problem with the commit, you need to fix it. You can commit to the same branch; the PR will be updated automatically.

## General notes about Pull requests

 * Please create descriptive commits containing atomic changes. Use short commit messages (try 50 characters, max is 70 characters); longer commit messages are possible in the body of the commit message (separated from the subject by an empty line). See [5].
 * If you fix an existing GitHub issue, reference it in the commit message
   body, e.g. 'Fixes #41'.
 * If your Pull request does not refer to an existing GitHub issue, it is not
   necessary to create one (because GitHub will present the PR just like an
   issue).
 * You can rewrite the history of the commits in your branch using rebase,
   but don't rewrite the history before the first commit of your new branch.
 * We like to keep the history clean and prevent a lot of 'fix typo' messages.
 * If you rewrite the history of your branch you can force push those changes to your branch. The PR will be updated. See, e.g. [6].
 
## Links
 
 * [1] http://help.github.com
 * [2] https://google-styleguide.googlecode.com/svn/trunk/cppguide.html
 * [3] https://help.github.com/articles/fork-a-repo/
 * [4] https://help.github.com/articles/creating-a-pull-request/
 * [5] https://chris.beams.io/posts/git-commit
 * [6] https://developer.atlassian.com/blog/2015/04/force-with-lease/
