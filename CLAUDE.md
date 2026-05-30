# My continuous Gen AI learning repo
This is a repo containing setup and scripts for running recurrent scans of the literature, internet, news outlets, etc for new developments in my fields of interest.  That's gen AI in entperises, gen ai safety, agentic architecture, large scale regulated gen ai adoption, etc.

The scan runs when I tell it to, and should only survey the new developments since the last time the scan was run on this topic.  The scan cycles through topics.

So I use this repo as the place to store the scan results and the place to store the script that runs the scan.  After running the scan I commit and push.

## Development workflow

All code changes follow strict TDD with thin vertical slices:

1. Break every task into the smallest testable increment
2. Write a failing BDD test first (given/when/then)
3. Implement just enough to make it pass
4. Verify all tests pass
5. Move to the next slice

Do not anticipate features, add extra UI elements, create database tables, or build anything not yet needed. One slice at a time. Wait for the next instruction between slices.