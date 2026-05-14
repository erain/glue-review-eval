## Summary
This branch renames the `--since` and `--until` flags in the `glog` command to `--within` and `--before`, respectively.

## Issues
- [minor] README.md:0 — The documentation for the `--within` and `--before` flags could be improved for clarity. Fix: In README.md, add examples and explanations for the `--within` and `--before` flags to help users understand their usage and purpose.

## Suggestions
- [minor] README.md:0 — Consider adding a section for troubleshooting common issues, such as handling file rotation when using the `--follow` flag. Fix: In README.md, create a new section titled "Troubleshooting" and provide guidance on handling file rotation and other potential issues.

## Looks good
* The commit message is clear and descriptive.
* The changes to the flag names are consistent and follow a logical naming convention.

## Open questions
* How will the changes to the flag names affect existing users of the `glog` command?
* Are there any plans to add support for handling file rotation when using the `--follow` flag?
