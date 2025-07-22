# CHANGELOG



## v0.10.0 (2025-07-22)

### Feature

* feat: return json output with path ([`6d2dd87`](https://github.com/mbari-org/fastapi-vss/commit/6d2dd870efa935120dd025d991c3e6e841f57123))


## v0.9.1 (2025-07-20)

### Documentation

* docs: updated related work to more relevant repo ([`bd3b798`](https://github.com/mbari-org/fastapi-vss/commit/bd3b79853415fc2c2aac384efff2027197af9bae))

### Fix

* fix: return location of json output correctly and message about timeout ([`09019d1`](https://github.com/mbari-org/fastapi-vss/commit/09019d1f3390fe5e39e77aa0444dec56cab871b9))

* fix: GPU spawn for safe multiprocessing ([`7003888`](https://github.com/mbari-org/fastapi-vss/commit/70038887020bfa8df66c5a778d5ee3f043782475))


## v0.9.0 (2025-07-07)

### Build

* build: correct tag for cuda build ([`139b4d0`](https://github.com/mbari-org/fastapi-vss/commit/139b4d0399a71b26b01166061ce45829dd84bf59))

* build: remove arm64 build for cuda build ([`ab31f13`](https://github.com/mbari-org/fastapi-vss/commit/ab31f1342e8e991395f9bb3cb04bf9704e1999ba))

### Feature

* feat: trigger release ([`84049b1`](https://github.com/mbari-org/fastapi-vss/commit/84049b1feb261d659026445b0cb24cdd0dfa7918))

### Performance

* perf: add support for task execution through redis queue workers (#2)

This is a significant enhancement that adds:

Redis queue workers
Saves results to JSON output to a data mount
Multiple GPU execution for speed-up
Better logging
Tests for most endpoints
Health check for FastAPI-vss service ([`d6cc7ba`](https://github.com/mbari-org/fastapi-vss/commit/d6cc7bac1113841eb1cebe7fd6085d6c49853300))


## v0.8.0 (2025-06-03)

### Feature

* feat: bump to mbari/aidata:1.55.1 ([`5efc603`](https://github.com/mbari-org/fastapi-vss/commit/5efc60399a57c69a1363f6ff26b88794be3aca71))


## v0.7.0 (2025-06-02)

### Feature

* feat: bump to mbari/aidata:1.53.0 and try cached build ([`aa35945`](https://github.com/mbari-org/fastapi-vss/commit/aa35945402b5ee06848f1b951b83236c3a1d12be))


## v0.6.0 (2025-06-01)

### Build

* build: updated release gh action ([`26b2a72`](https://github.com/mbari-org/fastapi-vss/commit/26b2a722e90dba75227b04fc19a3373046faf3fd))

### Feature

* feat: only added doc, but triggering release workflow for test ([`80cc0f9`](https://github.com/mbari-org/fastapi-vss/commit/80cc0f90a16a0e0093e15bac85bcf17011d9646d))


## v0.5.0 (2025-06-01)

### Build

* build: ignore code from base image ([`09d4955`](https://github.com/mbari-org/fastapi-vss/commit/09d49552e3ac72efb3acb6af34f05ac56b4a1b85))

### Documentation

* docs: remove installation ([`401edf1`](https://github.com/mbari-org/fastapi-vss/commit/401edf10c95cef888a23dbe62414ea8c60fc1efd))

* docs: minor rearranging ([`0a1b69d`](https://github.com/mbari-org/fastapi-vss/commit/0a1b69dbcf5103215358c836569a8aad98345b8d))

* docs: updated README.md with features and icons consistent with other docs ([`9a1e470`](https://github.com/mbari-org/fastapi-vss/commit/9a1e4702ac7083a72cd68a7f8f2467a02dcc2f34))

### Feature

* feat: bumped to aidata:1.53.0 ([`5cbed72`](https://github.com/mbari-org/fastapi-vss/commit/5cbed72434e5246a12cd85fe168d3cfca7b270f4))


## v0.4.6 (2025-06-01)

### Build

* build: bumped base to aidata:1.41.9 and added cuda124 to just recipe ([`47d5d52`](https://github.com/mbari-org/fastapi-vss/commit/47d5d5295593737325520625e385cee742a75181))

* build: bumped docker base and added recipe for docker build and push with provenance and SBOM ([`ea525dd`](https://github.com/mbari-org/fastapi-vss/commit/ea525dd02c19f8a8028603374abee662b413e474))

### Documentation

* docs: updated restup image to link ([`33eba86`](https://github.com/mbari-org/fastapi-vss/commit/33eba8618770ffeed7ac110a9648e88e52deedcb))

* docs: updated ui image ([`fdde441`](https://github.com/mbari-org/fastapi-vss/commit/fdde441df62a9ae7dba40574aa92bab482096930))

### Performance

* perf: allow BATCH_SIZE setting through environment variable BATCH_SIZE for optimized GPU performance; default 32 ([`8c259ee`](https://github.com/mbari-org/fastapi-vss/commit/8c259ee09722375db87839a3ee21aad7c9243f2d))


## v0.4.5 (2024-10-28)

### Performance

* perf: added GPU monitoring and pass through number of workers for improved redis performance ([`cfe8f6d`](https://github.com/mbari-org/fastapi-vss/commit/cfe8f6ddc4bc36b3f6377c7b95349661866bc112))


## v0.4.4 (2024-09-30)

### Performance

* perf: added garbage collection, increase batch size and multiple workers for higher throughput ([`bad00b9`](https://github.com/mbari-org/fastapi-vss/commit/bad00b9403738d64fa70e1b7e14aedb02d9382ad))


## v0.4.3 (2024-09-30)

### Performance

* perf: default to cuda ([`b8e14a5`](https://github.com/mbari-org/fastapi-vss/commit/b8e14a53263723381446b71136c7768462b5036c))


## v0.4.2 (2024-09-30)

### Fix

* fix: handle any prediction exception ([`64e8f96`](https://github.com/mbari-org/fastapi-vss/commit/64e8f96ef4a24fdb9acb356efd6f1d6f7287df6e))


## v0.4.1 (2024-09-16)

### Fix

* fix: bump version and updated docs with latest ui screen capture ([`2399296`](https://github.com/mbari-org/fastapi-vss/commit/23992969ce70c7d819bb7a3e4689f4f3f567ee23))


## v0.4.0 (2024-09-16)

### Feature

* feat: switch to vss project config name ([`be4d0bb`](https://github.com/mbari-org/fastapi-vss/commit/be4d0bb669711b907cee792f47659b448a056728))


## v0.3.1 (2024-09-06)

### Fix

* fix: fix typo ([`b5c9735`](https://github.com/mbari-org/fastapi-vss/commit/b5c9735dbde1b34276b3799fbdb8338ce44fc9e9))


## v0.3.0 (2024-09-06)

### Feature

* feat: add support for different models ([`53743ff`](https://github.com/mbari-org/fastapi-vss/commit/53743ff9b01a8bc0d038943ab999fc2f68f4fb3d))


## v0.2.1 (2024-09-04)

### Performance

* perf: bump to better indexing ([`7beb4b7`](https://github.com/mbari-org/fastapi-vss/commit/7beb4b72a08186ca89f540262f054904509db9c0))


## v0.2.0 (2024-08-28)

### Feature

* feat: change to external config_path via environment variable CONFIG_PATH ([`352dc6b`](https://github.com/mbari-org/fastapi-vss/commit/352dc6bddfa5fa4b3fe0656324ef63bd53d05251))


## v0.1.4 (2024-08-28)

### Fix

* fix: trigger CUDA release with updated docker build ([`dfb6838`](https://github.com/mbari-org/fastapi-vss/commit/dfb68381d8a7ea445394e2dc53aae11ea1cd6c95))


## v0.1.3 (2024-08-28)

### Fix

* fix: add missing dependency ([`5f0c861`](https://github.com/mbari-org/fastapi-vss/commit/5f0c86100caabc7f2e771a9f7dde4e4e87e9eca2))

### Unknown

* Update README.md ([`1a1b260`](https://github.com/mbari-org/fastapi-vss/commit/1a1b2609f4c663adb8bbc9b5c6e4b59c40fded7e))


## v0.1.2 (2024-08-22)

### Fix

* fix: trigger release to update __init__.py ([`65e3ecd`](https://github.com/mbari-org/fastapi-vss/commit/65e3ecdde528fb222bc349a9cae6c3c7c632f0a8))


## v0.1.1 (2024-08-12)

### Fix

* fix: correct handling of .env ([`17c2de0`](https://github.com/mbari-org/fastapi-vss/commit/17c2de03d4bab636364a2def0399202b73de50b1))


## v0.1.0 (2024-07-30)

### Documentation

* docs: minor fix to link ([`f86a56a`](https://github.com/mbari-org/fastapi-vss/commit/f86a56acbf2022420f98b0ea2e33aa7a5c352265))

### Feature

* feat: added project and knn api and aidata submodule ([`dc736e1`](https://github.com/mbari-org/fastapi-vss/commit/dc736e181c18818a8f73131c2bfc81cdd27e7088))

* feat: added aidata submodule ([`ac509e1`](https://github.com/mbari-org/fastapi-vss/commit/ac509e19618b15b3489f6e4ec229097adabacf06))

* feat: initial commit ([`ae974a4`](https://github.com/mbari-org/fastapi-vss/commit/ae974a4aeeb5e2084b46ff27e2d18513708fff23))
