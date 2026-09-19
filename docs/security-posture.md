# Security posture

Rewritten from the Security section of `fcaps-parity-with-ems.md`, whose
central premise — that these devices are SNMPv2c-only and cleartext
communities are therefore unavoidable — is wrong for the switch.

## The switch supports SNMPv3. Use it.

`ML540M-SNMP-MIB` (67 objects, one of the 30 modules absent from the original
attribute schema) defines a complete USM/VACM implementation:

```
VTSSSnmpVersion       ::= INTEGER { snmpV1(0), snmpV2c(1), snmpV3(2) }
VTSSSnmpSecurityLevel ::= INTEGER { snmpNoAuthNoPriv(1), snmpAuthNoPriv(2), snmpAuthPriv(3) }
VTSSSnmpAuthProtocl   ::= INTEGER { snmpNoAuthProtocol(0), snmpMD5AuthProtocol(1), snmpSHAAuthProtocol(2) }
VTSSSnmpPrivProtocl   ::= INTEGER { snmpNoPrivProtocol(0), snmpDESPrivProtocol(1), snmpAESPrivProtocol(2) }
VTSSSnmpSecurityModel ::= INTEGER { any(0), v1(1), v2c(2), usm(3) }
```

with `ml540mSnmpConfigUserTable` (engine ID, username, security level, auth
protocol and password, privacy protocol and password),
`ml540mSnmpConfigAccessGroupTable` and `ml540mSnmpConfigViewTable` — all
creatable through the row-editor mechanism already proven.

**So cleartext SNMP on the switch is a configuration choice, not a platform
constraint.** Target: SNMPv3 `authPriv` with SHA + AES. Prefer AES over DES
and SHA over MD5 where both are offered.

The DSL side is less clear. `ML600_MIB.7z` ships `SNMP-FRAMEWORK-MIB`
(`snmpEngineID`, `snmpAuthProtocols`, `snmpPrivProtocols`), which is the
SNMPv3 framework MIB — suggestive, but it is a standard file that could be
present purely as a dependency. `ML620R-MIB` exposes plain
`readOnlyCommunity` / `readWriteCommunity` / `trapCommunity` scalars. Treat
ML600-family SNMPv3 support as **unknown pending a lab check**, not as absent.

## Findings that stand from the original

**Factory-default communities are live.** The lab ML540M answers to
`public` / `private`. That is flagged in the original and it is right to flag
it — but it is still true, on a unit that accepts writes.

**The write community is readable with the read community.** The original
presents this as a useful bootstrap pattern — "query the device's own config
to discover its write community rather than guessing" — and operationally it
is. It is also a genuine finding in its own right: *a read-only community
discloses the read-write community.* Anyone who obtains RO access obtains RW
access. On SNMPv2c with a default RO community, that is the whole security
model gone.

Objects concerned:
`ml540mSnmpConfigGlobalsWriteCommunity` (`1.3.6.1.4.1.5468.100.36.1.2.1.4.0`)
and `readWriteCommunity` (`1.3.6.1.4.1.5468.510.2.13.1.1.3`) on the modem.

**Source-IP-restricted communities exist.** `ml540mSnmpConfigCommunityTable`
scopes which management hosts may talk to the agent at all — the same table
used for the row-editor proof. `ML540M-ACCESS-MANAGEMENT-MIB` (53 objects,
also uncovered) adds per-service management ACLs.

## What this repo changed

* **No credentials in the repo.** `etc/devices.yaml.example` names
  environment variables; the original committed `public`/`private` inline.
  `etc/devices.yaml` is gitignored.
* **Community strings off the command line — optionally.**
  `community_mode: snmp_conf` writes a `0600` `snmp.conf` and points
  `SNMPCONFPATH` at it, so the community is not visible in `ps` to every
  local user on the management host. This matters because the write community
  is in play.

  **It is not the default, and it has not been verified against a live
  device** — net-snmp was not installed where this was written. Verifying it
  is a lab task (below). Shipping an unverified credential path as the default
  would repeat the mistake the missing trailing `.0` taught.
* **Authorization failures are never retried.** Retrying a rejected
  credential is how lockouts happen on AAA-backed devices.

## Lab checklist

1. **Change the lab unit's communities off the factory defaults.** Then
   restrict via `ml540mSnmpConfigCommunityTable` — a genuinely useful first
   production use of the row-editor helper.
2. **Prove SNMPv3 authPriv on the switch**: create a USM user via
   `ml540mSnmpConfigUserTable`, set `ml540mSnmpConfigGlobalsVersion` to
   `snmpV3(2)`, and confirm `snmpget -v3 -l authPriv` works. If it does, the
   posture for the whole switch estate changes.
3. **Determine whether the ML600 family supports SNMPv3** —
   `snmpwalk -v2c -c "$RO" <modem> 1.3.6.1.6.3.10.2.1` (snmpEngine) is the
   quickest probe.
4. **Verify `community_mode: snmp_conf`** against the local net-snmp build,
   then make it the default if it works.

## Open questions

* Does NSP provision device-level AAA (local users, RADIUS/TACACS+) as part
  of a v1 adaptor, or is that a separate ZTP/bootstrap concern? Asked.
* Does NSP's Communicator support SNMPv3 USM for third-party adaptors, and
  how are credentials stored? Asked — and materially more important than the
  original's "what's your position on managing SNMPv2c-only devices", which
  was premised on a constraint that does not exist for the switch.
* Is there an OOB management network for this estate, or does SNMP share the
  service path? Decides how much the above matters.
