# Trust Boundaries

> A vulnerability is a boundary crossing that the design did not intend. If you cannot name the
> boundary, you cannot name the vulnerability.

## 1. Boundary catalogue

| Boundary | Lower-trust side | Higher-trust side | Typical failure |
| --- | --- | --- | --- |
| Network edge | Internet client | App server | Missing authn, input trusted as parsed, rate limits absent |
| Authentication | Anonymous request | Authenticated principal | Token confusion, algorithm confusion, session fixation |
| Authorization | Authenticated user | Another user's / tenant's data | IDOR, missing ownership check, client-supplied tenant id |
| Privilege | Regular user | Admin function | Role checked in UI only, not server-side |
| Process | Child process / plugin | Host | Command injection, unsafe deserialization, path traversal |
| Storage | App query layer | Database | String-built SQL, over-broad DB role, missing row-level policy |
| Serialization | Serialized bytes | In-memory object | Gadget chains, type confusion, unsafe polymorphic deserialization |
| Build/supply chain | Third-party package | Build artifact | Typosquat, compromised maintainer, install-time script |
| Tenant | Tenant A | Tenant B | Shared cache key, missing tenant predicate, cross-tenant index |
| Secret | Runtime process | Config/log/artifact | Secret in env logged, secret in error, secret in image layer |
| Human | Support/operator | Customer data | Over-broad admin tooling, missing audit trail |

## 2. Actors

For each, write what they can reach *today* and what they should reach:

- **Anonymous** — no credentials, can send arbitrary bytes.
- **Authenticated user** — valid session, may be malicious, may control their own input fully.
- **Cross-tenant user** — valid session in another tenant; the most under-modelled actor.
- **Insider / operator** — legitimate access, possibly over-broad, possibly phished.
- **Supply chain** — anyone who can influence a dependency, build step, or update channel.
- **Physical / local** — only relevant for client-side or device threats.

## 3. Boundary questions

For each boundary the change touches:

1. What exactly crosses it (data, command, identity, capability)?
2. Who validates the crossing, and is that validation on the server side?
3. What is the trust assumption after the crossing — and is it documented or implicit?
4. Can the lower side choose *which* object on the higher side to act on?
5. What happens when the validation is bypassed: fail-open or fail-closed?
6. Is the crossing logged with enough context to investigate later?

## 4. Modelling discipline

- Draw the boundary before reading the code. Reading first biases you toward the author's assumptions.
- An "internal" service is not automatically trusted: internal networks are reachable after a single
  foothold, and service meshes do not authenticate business intent.
- Client-side checks are UX, never security. Any check that runs on the attacker's machine is advisory.
- Secrets are a boundary: anything in a container image, log line, or error message has crossed it.

## 5. Reachability record

For each candidate finding, write a five-line record:

```text
Actor:        <who, with which credentials>
Entry:        <endpoint/handler/file read/queue topic>
Precondition: <configuration, feature flag, data state>
Path:         <functions/modules traversed, in order>
Blocked by:   <control found, or "none">
```

If any line is `unknown`, the finding is at most `LIKELY`, and the check that would resolve it must be
named.
