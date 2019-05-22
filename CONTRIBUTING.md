# How to contribute

## Testing

Testing is not yet automated. Hopefully you will see this section change in a git commit very soon..
however..

Please add your tests to the script located here: ``tests/functional/run-tests.sh``. Ensure that
your tests pass before making a PR in the repository.

To run lint tests you can utilize tox: ``tox``  
The plan is to expand our unit testing and functional testing utilizing Tox so that we can
ensure our changes are good. Unfortunately we do not have this implemented yet.


## Submitting changes

Piedpiper utilizes [Trunk-Based Development](https://trunkbaseddevelopment.com/)

Please submit your change as a PR from a feature-branch in your fork.

Please send a [GitHub Pull Request to PiCli](https://github.com/AFCYBER-DREAM/piperci-picli/pull/new/master) with a clear list of what you've done (read more about [pull requests](http://help.github.com/pull-requests/)). When you send a pull request, we will love you forever if you include RSpec examples. We can always use more test coverage. Please follow our coding conventions (below) and make sure all of your commits are atomic (one feature per commit).

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    > 
    > A paragraph describing what changed and its impact."
    
Here is what the workflow might look like:
1. Submit issue.
2. Create fork of piperci-picli.
3. Create a feature branch for your issue on on your fork.
4. Iterate on your change, keeping it as small as possible.  
4a. Optionally create a WIP pull request describing your change.
5. Open a pull request

Once your pull request has been reviewed and signed off it will be merged into master.

## Coding conventions

PiCli attempts to adhere to PEP8 as much as possible. However, some standards
are not followed. For example, the 79-character line length rule is not observed.

See our .flake8 file for the excluded standards.


