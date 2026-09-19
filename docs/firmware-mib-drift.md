# Firmware and MIB drift

The estate will not run one firmware version, and the vendor MIBs will not
match every agent. This is already demonstrated rather than hypothetical:
firmware `00.00.16` on the lab ML540M does not implement
`ml540mLldpStatusNeighborsInformationTable` at all, despite LLDP being
administratively enabled on all ten ports. The response was `No Such Object`
— the branch does not exist on the agent — not an empty table.

Three distinct kinds of drift, which need different handling.

## 1. Agent implements less than the MIB says

The LLDP case. The MIB is the vendor's statement of intent; the agent is what
actually shipped. Detection is at runtime.

**Handled:** `SnmpNoSuchObject` is a distinct exception, never retried, and
recorded once per device per OID in the `capability_gaps` table rather than
re-logged every cycle. Inspect with:

```bash
actelis-mediation --config etc/devices.yaml show --device lab-switch-01
```

**Still to build:** a per-firmware capability matrix, populated from the first
walk of each new firmware version encountered. That is the artefact that lets
you answer "will this adaptor work on the production build" without guessing.

## 2. Vendor MIB revisions move things

A new MIB package can renumber a column, add an index component, or relocate a
subtree. Silent, and catastrophic for a poller: the OIDs still resolve, they
just mean something else.

**Handled:** `tests/test_mib_conformance.py` re-derives every OID and index
spec from the archives on every CI run. Drop in a new `.7z` and the suite
fails with the specific object that moved. This is why the OID constants live
in one annotated module (`poll/oids.py`) rather than inline.

## 3. Different models, different MIB surfaces

The ML600 family is one MIB package covering 53 model variants
(`ACTELIS-SERV-MON-MIB`'s `Models` enum — see ADR-0003). They will not all
implement the same subset.

**Approach:** discover the model from `servMonSystemModel` at discovery time,
then treat per-model differences as capability detection rather than as
separate device types. Record what each model actually implements.

## Vendor MIB bugs

`ACTELIS-SERV-MON-MIB` has a genuine SMIv2 authoring bug —
`servMonMEPLossFLFLR1DayELANEntry ::= { servMonMEPLossFLFLR1DayELANTable 2 }`
where SMIv2 requires `1`. Independently confirmed: it is the only such
violation in the file.

The original's judgement that this is cosmetic is probably right, but it is
worth being precise about *why* it is uncertain: the MIB source says the row
lives at `...Table.2`, and standard tooling says it must be at `...Table.1`.
Which one the agent actually implements is an empirical question nobody has
answered, because no ML600-family unit has been reachable. If the agent
follows its own MIB, a poller built from a corrected file walks the wrong
OID and silently gets nothing.

**Practical handling:** the local fix is applied only in the extraction tool,
the vendor file in `mibs/actelis/` is untouched, and the question is asked
explicitly (Actelis question 4). Resolve by walking both
`...Table.1` and `...Table.2` on the first available unit — two commands.

## Practices this implies

* Never hand-copy an OID into code. Add it to `poll/oids.py` with its object
  name and let conformance testing check it.
* Keep the original vendor archives in the repo, unmodified. They are the
  evidence base, and every generated artefact is reproducible from them.
* When a new firmware appears in the estate, walk it before trusting it, and
  record the result.
