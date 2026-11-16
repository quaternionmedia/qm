# What the installs reach: two strace runs

*Every host two of apothecary's installers reached, traced with `strace` on a
real install, and what a build or a slice reached afterwards. The host lists
are `RUST_INSTALL_HOSTS` and `SLICER_INSTALL_HOSTS` in
`tests/test_stays_local.py`, which hold each one to the install-time list
`stays_local.TOOL_SOURCES`; this record keeps the runs they came from, as they
were recorded beside those lists when they were written.*

## 2026-10-09: `apothecary firmware install --rust-esp32`

| Host | Reached by |
|---|---|
| `static.rust-lang.org` | apothecary's fetch of rustup-init and its `.sha256` |
| `api.github.com` | apothecary's fetch of the SHA-256 GitHub publishes for espflash's asset and the Xtensa Rust and rust-src archives, whose release has no checksum file |
| `github.com` | apothecary's fetch of espflash and of Espressif's Xtensa Rust, rust-src, LLVM and GCC archives, and the checksum files their releases publish |
| `release-assets.githubusercontent.com` | the redirect for each release asset |
| `index.crates.io` | `cargo vendor` reading the sparse index for each locked crate |
| `static.crates.io` | `cargo vendor` downloading each locked crate |

A build of `parts/esp32_blink/rust` afterwards reached no host.

## 2026-10-10: `apothecary slicer install`, OrcaSlicer 2.4.2 on Linux x86_64

| Host | Reached by |
|---|---|
| `api.github.com` | the SHA-256 GitHub publishes for the pinned release's asset |
| `github.com` | the pinned release's asset |
| `release-assets.githubusercontent.com` | the redirect for the asset |

A slice afterwards reached no host: OrcaSlicer asked the resolver nothing and
connected nowhere.
