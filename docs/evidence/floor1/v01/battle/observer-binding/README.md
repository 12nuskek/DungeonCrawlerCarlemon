# Current active-pose observer binding: offline only

Implemented and compiled; source/static and synthetic unit checks pass. Runtime
remains blocked; draft PR114 is unmerged. Screenshots N/A: no game execution or
captures in this increment. Tested game source is
`9c83611e8e9b61d55388c18496c361d3362e462e`, published parent
`85de0d54eddd3fb60e803831f74ca9ce9e28b54c`, engine tree
`8d8c7761f4878bb9a8d7e2bffe36ed38da08aa6a`.

## Separation from gameplay preparation

The existing `scripts/floor1/v01-battle-host.py.generate` reads source from Git
and headers, and requires no Save. The existing gameplay runner's `main` checks
the Save hash before its `--prepare` branch; `fixtures` calls
`guard-first-state.seed_snapshot` to decode that Save into expected party,
flags, resources, context and friendship-counter files. Those operations are
necessary for gameplay preparation, not source-only generation/ELF binding.

The new `scripts/test-f1-v01-observer-binding.py` separately generates the same
host, compiles it once, and exports native symbols from the current ELF. The
host binary is never invoked. It creates no Save, prepared route or runtime
expected stream. Existing gameplay runner, retained-reference verifier, host,
observer, strict comparisons, state assertions, route and engine are unchanged.

## Observed checks and identities

[Binding result](binding-result.json) records 85 effective observer bindings,
15923 canonical functions, 11 unique scoped lifecycle functions and 11 missing
lifecycle rejection cases. All 21 passive timeline points export. Native entry
`0x080008ac`, unique AgbMain BL `0x080004ba`, caller LR `0x080004bf`, entry opcode
`0xb500`, preceding play-time/music call order and exact compiled instructions
pass. Actual native headers compile all 13 existing layout assertions, 18 ABI
constants and six bitfield objects; compiled values match the prior audit.

| Artifact | SHA256 |
| --- | --- |
| Generated unchanged observer source | `1647352d92b3fa6f0135cf80f4c48df1c2a8a3818b711fd94651390a6334977f` |
| Newly compiled observer binary | `a17ea5134e700efd77552d9a279fd4d6dd94294d443683b8e9fbfe142361ccbd` |
| Bound active-pose ELF | `98fc1accd7516fb54baf15ba76cb954ca24a30051dfea63704a0efcf2882c53d` |
| Current symbol export | `91034ec5f80eb97d64a7325d0a5bcd4ef1593c3942f9a435059ef9843de5d069` |

The source and binary match the previously recorded host identities. This is a
new offline binding result against the active ELF, not transferred runtime
acceptance. No game rebuild was performed. The existing active ROM pin remains
`6b7a83f27ede2dac9a124c0e267f34c9d0747db4a68cff05425fb9966f5b2459`;
this increment did not open it.

The inherited raw-name parser has two explicit limitations. Four old probe
symbols are absent; their `policy` command fails closed and is unused by the
frozen route. `Task_DisplayHPRestoredMessage` occurs in both Softboiled and party
menu source. The existing ordered parser's final assignment is verified as
`L:party_menu.o:Task_DisplayHPRestoredMessage` at `0x081b63ec`. Global raw-name
uniqueness is not claimed. No symbol was silently rerouted or production gate
relaxed.

## Sleeping age and unchanged observer expectations

[Age result](age-result.json) records one ordinary host-C unit execution with
14 synthetic cases using current pose source and the unchanged observer. All
17 authored pixel arrays are checked against this ELF. Existing native-event
stubs and observer setup/read stubs are reused; capture is the existing no-output
stub. No emulator is linked or invoked. These are not reconstructed inputs or
historical/runtime captures.

For trainers858/859, native WINDUP remains active at age17, reaches18 before
sleeping, freezes a successful hold, and survives notification/another actor's
animation. The observer still requires pose14 when WINDUP age>=18 and returns
STOP108 for wrong held-warning pixels. REST settles after its final copy and
freezes unused age. The full2560-byte snapshot excludes pose state exactly as
before; no byte comparator is narrowed. Retirement still rejects any stale
byte among all16 pose bytes, including age alone, with STOP105. Actual source
reset then permits synthetic retirement and field lifecycle completion. These
checks do not prove native runtime cleanup.

## Reproduction and remaining gates

Use the current local pinned toolchain and active engine build:

```text
python3 scripts/test-f1-v01-observer-binding.py --engine <active-engine> --tool-root <local-tool-root> --output <new-offline-directory>
python3 scripts/test-f1-v01-observer-age.py --engine <active-engine> --output <new-unit-directory>
```

Diagnosed initial offline tooling failures and resumed work are recorded in
the result files. Host compilation completed once; age fixture compilation
had two include-search failures and one success, followed by one unit execution.
No generated host invocation, ROM/Save load, emulator, replay, new reference
stream, game build, download/upload retry, environment change or merge occurred.
Historical execution totals remain six baseline/four candidate.

The finalized candidate archive's single supported download failed before any
local bytes were produced and remains recorded privately. Ordinary Save bytes,
the complete original raw reference/expected-boundary stream, and original
legacy inputs remain unavailable. No recovery, ordinary-input acceptance,
legacy substitution or new runtime acceptance is claimed. Previous failures,
controllers and strategy records remain unchanged. Historical status/plan files
and denied private-history material are untouched.

Next dependency-ready step is parent review of this source-only binding and age
evidence. Gameplay and recovered-input validation remain blocked pending exact
input recovery and separate authorization. Existing legacy/C01/human-pacing/
full-floor limitations remain.
