# Versioning and Compatibility

**Status:** Foundation 0.1  
**Applies to:** Mission Core schemas, examples and future API contracts

## Purpose

Mission Platform must evolve without silently changing the meaning of existing mission models. Versioning therefore applies to machine-readable contracts as well as documentation.

## Version format

Mission Platform uses `MAJOR.MINOR` contract versions during the Foundation phase.

- **MAJOR** changes may alter meaning, remove required behaviour or make previously valid models invalid.
- **MINOR** changes add backward-compatible capabilities, optional properties or clarifications.

Patch-level corrections may be represented by repository tags and release notes when they do not change the contract identifier.

## Schema identity

Every Mission Core document declares `schemaVersion`. Published schemas live in a versioned path:

```text
schemas/mission-core/<major>.<minor>/mission-core.schema.json
```

A published schema is immutable. Corrections that affect validation or semantics require a new version.

## Compatibility rules

A newer implementation may read an older Mission Core document when it:

1. validates the document against the schema version declared by that document;
2. preserves identifiers, provenance, ownership and temporal meaning;
3. does not invent missing facts without recording new provenance;
4. reports any lossy transformation before migration;
5. retains the original source document or a verifiable reference to it.

## Change classification

### Backward-compatible

- adding an optional property;
- adding a new optional element type;
- clarifying prose without changing validation;
- adding an enum value only where consumers are required to tolerate unknown values.

### Breaking

- removing or renaming a property;
- changing a property type;
- adding a required property without a defined default or migration rule;
- narrowing an allowed value set;
- changing the normative meaning of an element or relationship;
- changing identity, provenance or time semantics.

## Deprecation

Deprecated properties or relationship types must remain documented for at least one subsequent minor version. Deprecation notices shall identify:

- the replacement;
- the reason;
- the first deprecated version;
- the earliest possible removal version;
- migration guidance.

## Migration records

A migration must produce a record containing source version, target version, migration method, timestamp, actor, warnings and validation outcome. AI-assisted migrations must declare that assistance and retain human accountability for approval.

## Foundation 0.1 stability statement

Foundation 0.1 is an experimental contract intended for implementation learning. It establishes stable principles for identity, traceability, provenance, ownership and time, but individual field names and structures may change before 1.0.
