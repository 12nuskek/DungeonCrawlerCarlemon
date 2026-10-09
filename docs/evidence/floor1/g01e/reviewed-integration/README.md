# Reviewed stack integration — 9 October 2026

All 20 reviewed PRs through PR110 are merged using ordinary merge commits.
Final main: `a83777b94684919d121cabf4f6b2d45de23027c7`.
Initial main: `b694da17928b93ea579f55d905017aa9f7619422`.
Kurt's existing sequential integration authority followed parent review of PR110.
This increment integrates the reviewed stack and checks build identity. It performs
no new emulator execution or art work.

## Verified sequence and identities

Each successor was retargeted to main only after its predecessor's merge was
confirmed. Each retargeted binary patch matched its reviewed original delta by
SHA256; merge-tree predicted the exact head tree without conflicts. Each real
merge was fetched and checked for two parents (previous main, original head),
the exact original full tree and engine tree, and unchanged original head.
GitHub's merged PR metadata was independently checked before advancing.

| PR | Verified main base | Original head | Tested host or audit | Verified merge |
| --- | --- | --- | --- | --- |
| [75](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/75) | `b694da17` | `16d7012b` | `1e556a25` | `9557bc0e` |
| [77](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/77) | `9557bc0e` | `ce43420b` | `821e0733` | `c7f47475` |
| [79](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/79) | `c7f47475` | `91a4b79b` | `c643f01c` | `30080aa6` |
| [81](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/81) | `30080aa6` | `7866c873` | `2ae9d148` | `5a33575a` |
| [83](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/83) | `5a33575a` | `a9658676` | `477e5055` | `463c3e78` |
| [85](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/85) | `463c3e78` | `f4e568d5` | `0317dc8c` | `5223b0df` |
| [87](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/87) | `5223b0df` | `00a31be5` | `fa175347` | `d432899a` |
| [89](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/89) | `d432899a` | `f8178113` | `db085577` | `1df3d182` |
| [91](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/91) | `1df3d182` | `b36f750c` | `7d89fcdd` | `b26865f8` |
| [93](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/93) | `b26865f8` | `1263d8b9` | `cc384576` | `0e56c462` |
| [95](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/95) | `0e56c462` | `e0d75cc3` | `7197e785` | `f5e55edd` |
| [97](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/97) | `f5e55edd` | `ed519a05` | `dd349a2e` | `fd5579ad` |
| [99](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/99) | `fd5579ad` | `61fba93c` | `a31355a2` | `50d02e4e` |
| [101](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/101) | `50d02e4e` | `531276ae` | `a9e73074` | `9783bb11` |
| [103](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/103) | `9783bb11` | `1e81d129` | `8a3f598c` | `1c152c90` |
| [105](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/105) | `1c152c90` | `84cbb196` | `5cdc77a4` | `a8e443a6` |
| [107](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/107) | `a8e443a6` | `1663abb0` | `514187f6` | `780ab00c` |
| [108](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/108) | `780ab00c` | `3e0ace22` | `ba2237c8` | `848c79a9` |
| [109](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/109) | `848c79a9` | `4eb46e72` | `cad9eadf` | `2016782e` |
| [110](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/110) | `2016782e` | `6c7f2e10` | `8a21c95f` | `a83777b9` |

Full base/original/tested game, host, execution and merge SHAs, patch hashes,
merged timestamps and per-step checks are in [reconciliation.json](reconciliation.json).
A tested host is not a publication head; failed execution remains failed.
The linked original evidence gives complete route/source/capture identities.

All 64 existing branches remain; all 63 non-main heads are unchanged. No original
head was edited, no branch deleted, and no squash/rebase/force/protection bypass
occurred. Automatic branch deletion was disabled and remained unchanged.
Final main's full tree equals original PR110 `6c7f2e10f861b0518da3e7841e523433b2a1b451`.
The complete accepted plan remains unchanged at SHA256
`9b3e5d6f607a5345f73ea06dc38211d1c1a085bcd1d505a5772d4fb88e71ef27`.

## CP72e bridge

PR91's retargeted diff contains both the 21-file reviewed bridge
`f8178113b42cdf14f5540ecd50268df5da8a947f` →
`72e08ed17afc69e28ef545bbbff383a434e90df5` and its recovery delta.
There is no duplicate current-patrol PR. CP72e is verified an ancestor of PR91's
merge `b26865f8127656732dbb01260bb1394ac0bdc211`, every subsequent merge and final
main. Bridge engine diff is empty; original c643/b025/c7c5 evidence (81 assertions,
two sessions, eleven actual captures) remains historical evidence from unavailable
original inputs. It does not transfer acceptance to reconstructed files.

## Checks and protections

Fresh branch/PR/check/status/workflow/review reads preceded each merge.
Main reported `protected:false`, status enforcement off, no required contexts/checks,
and no rulesets. The administration-only protection endpoint returned 403
“Resource not accessible by integration”; this permission limitation was retained,
not bypassed. Ordinary GitHub merge calls enforced server rules with exact expected
heads. No mandatory approval, conflict or unreviewed diff appeared. Brief unknown
mergeability after retargeting was resolved by read-only queries before merging.

No check runs, commit statuses or Actions runs were returned on any reviewed head,
or on final main at the final read. The all-event Actions query used exact head SHA;
the PR-only first-page helper was not used as proof of global CI. Empty results
mean **absent CI**, not CI success. Parent review in the conversation is separate
from GitHub review records, which were empty.

## Build and evidence boundary

Integrated engine tree `46e5f0f58684e61719c08ad4909b4727b0ca0af9` equals approved
game `5084a1814904f1a43fd999fddf770b221bb53653`.
See [build identity](build-identity.json) for the fresh integrated-main compilation,
pinned tooling and exact ROM comparison. No broad emulator replay is appropriate
for this unchanged engine; this build does not create new runtime acceptance.
Original evidence remains source- and input-qualified.

The [corrected Guard-first package](../guard-first-corrected/README.md) retains
164 route +18 cold assertions, six measured legs, exact native manual Save/cold,
13 actual captures, 52 controller and 32 HP records. Frozen execution 8a21c95f
and game 5084/ROM 23c77 are unchanged. PR109 STOP71, prepared cold STOP57, original
Warden loss, all three historical patrol strategy failures and controller records
remain byte-identical. Their separate closures never rewrite failed executions.

New ordinary inputs and necessary raw evidence remain in existing supported private
ChatGPT Library backups. No ROM/save/raw native context/key/denied dataset is added
to Git. Current corrected Save SHA256
`030b12fd3516351b0935b9298f24d0a2078fb33afecbccb6ba3a9b4c2db6b73c`
is at arena approach 35.3/8,7 (Potion 1), and is distinct from reconstructed Howler-first
Field 37,31 Save 026c16fe…23220a (Potion 0) and the unavailable original patrol input.
[Retention inventory](private-retention.json) records existing archive identities;
integration performs no new Save execution or private dataset recovery.

Original 16 legacy saves, original raw logs/patrol-complete input and deleted-task
exclusive claims remain missing. The original legacy-input reproducibility gate
is unavailable, not waived or satisfied by fresh inputs. C01 uninterrupted opening,
timing/human pacing, later districts and full-floor acceptance remain later gates.
No broad visual or full-floor rollout is claimed.

## Next dependency

Integrated main and parent-reviewed bounded G01e evidence are ready for parent
review of this integration checkpoint, followed by the separately scoped
[V01 pilot plan](../../../../floor1/v01-entry-plan.md). This documentation checkpoint
is published on its own branch/draft PR; it is not an additional main merge.
Screenshots for this nonvisual integration are N/A; actual source-bound captures
remain in the original evidence packages.
