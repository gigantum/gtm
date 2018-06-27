Contributing to the Gigantum codebase
=====================================

In general, the goal is to minimize effort for both Gigantum and outside
developers while doing all necessary due diligence to ensure a legally sound
open source project.

Please note that Gigantum is still in a beta period and the core team continues
to make significant changes to the codebase. Please [submit an
issue](https://github.com/gigantum/gtm/issues) prior to developing an intended
contribution so the Gigantum team can help make it easier to accept your work!

As with Docker and the Linux kernel, Gigantum uses the [Developer Certificate
of Origin](https://developercertificate.org/). This is lightweight approach
that doesn't require submission and review of a separate contributor agreement.
Code is signed directly by the developer using facilities built into git.

## Signing your commits

When you contribute to any Gigantum-managed repository (currently, any
repository under the `gigantum` organization on GitHub), you must certify you
agree with the [Developer Certificate of Origin](https://developercertificate.org/). 
You indicate your agreement by signing your git commits like this:

    Signed-off-by: Pat Smith <pat.smith@email.com>
    
To create a signature, you configure your username and email address in Git.
You can set these globally or locally on just your fork of a Gigantum
repository. You must sign with your real name.  You can sign your git commit
automatically with git commit -s. Gigantum does not accept anonymous
contributions or contributions through pseudonyms. 

For a more complete set of instructions that includes the above approach to
code-signing, please see the excellent [instructions on using git to submit
code to the moby repository](https://github.com/moby/moby/blob/master/docs/contributing/set-up-git.md).

## Copyright statements

The astute reviewer may note the presence of copyright notices at the head of
some files. While we currently see no value in the work of removing these
statements, no such statements should be placed in new files, and the removal
of such notices at the head of a file along with other meaningful contributions
will be accepted. A LICENSE file (which may optionally have an extension such
as .txt or .md) should be included in the base directory of any Gigantum
respository, and should be included with any significant distribution of
Gigantum code, data, or other licensed materials.

Currently, the MIT license is used for all Gigantum code, but in any case, the
current LICENSE file is authoritative.
