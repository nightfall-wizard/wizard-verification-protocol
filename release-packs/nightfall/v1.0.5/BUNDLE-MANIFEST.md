# WVP-SEC-010 - Nightfall Evidence Release Pack Manifest

This manifest defines the versioned WVP evidence bundle for Nightfall v1.0.5.

Boundary: this release pack is not an audit and not a certification.

Pack name: `wvp-nightfall-v1.0.5-evidence-pack`

Files: 155

## Safety boundary

- no_real_seed: `True`
- no_private_key: `True`
- no_live_funds: `True`
- no_exploit_payloads: `True`
- sanitized_public_report_included: `True`
- non_audit_boundary_required: `True`

## Excluded self-referential files

- `release-packs/nightfall/v1.0.5/BUNDLE-MANIFEST.json`
- `release-packs/nightfall/v1.0.5/BUNDLE-MANIFEST.md`
- `release-packs/nightfall/v1.0.5/SHA256SUMS.txt`
- `release-packs/nightfall/v1.0.5/wvp-nightfall-v1.0.5-evidence-pack.tar.gz`
- `reports/nightfall/v1.0.5/RELEASE-PACK.json`
- `reports/nightfall/v1.0.5/RELEASE-PACK.md`

## Bundle file list

| Path | Size | SHA-256 |
|---|---:|---|
| `.github/workflows/ci.yml` | 8591 | `955e3415045a65556f1414e372c5ce39440f3bc53def7bf78b918cdbfa02ce7d` |
| `.github/workflows/wvp-nightfall-security.yml` | 890 | `0eb7611c860176b2b41532de5de3147e934602c9e5bf6739d3e10d451cd826e8` |
| `.github/workflows/wvp-release-reality-check.yml` | 2176 | `a2d094fedd28a4a4044a6686d85ccf4b2a03953b3fe8baf1fc001cb72ad2703a` |
| `.github/workflows/wvp-required-checks.yml` | 1554 | `a7b734ebf9ab47c9794ccd599786b5a78b405c379111842ff7e3c3b0b41ac76c` |
| `PROJECT-STATE.md` | 5520 | `16eeda0e797205ad8a8801ad89dd045c149ebf76c51b6de7b17f79f15a768372` |
| `README.md` | 18647 | `1762535e1f9eb0c5803ee4c76e3c4cfbf92fa77ad1c08de513ddf0687d3b06b0` |
| `SECURITY.md` | 658 | `9dc600cc35d5ac66a512601a4c17629f1b853d7e502875f6a310155bced1f451` |
| `docs/CI-HARDENING-METHOD.md` | 824 | `15d7d44a6c6810cedb998d8c7814bd68f99568c5a96759b5ca5a25e74a35e853` |
| `docs/CODEPATH-BINDING-METHOD.md` | 666 | `b966ec2c332aa21420eacc823eaa1e03458c0e1c4c28b8ed38ceef7073ea8d90` |
| `docs/COMMAND-PROBE-METHOD.md` | 814 | `59ee9c78ad19bce09cf90fe8b121a0d9f6f35706a2becc573753c8c7416408fc` |
| `docs/CONFORMANCE-SCORING-METHOD.md` | 754 | `aa12e7fca81b130b1db4af3980f597015b4c29377fe018b8f8ef2c298af89b4b` |
| `docs/FINDINGS-TRIAGE-METHOD.md` | 759 | `8919af18cbcf3ce995febef01d01d705c446f4243ce892dd5e9cc3db0592066c` |
| `docs/NEGATIVE-VECTOR-METHOD.md` | 794 | `c3e07e0648ea0e9c4ee3371596a597b6795f75cbc7680dd919d8b0885a21701f` |
| `docs/PRIVATE-DISCLOSURE-METHOD.md` | 1077 | `2132fb092f75e0ce532092c877d7515f1df3986faf88b21dd277906281fff30d` |
| `docs/PUBLIC-REPORT-METHOD.md` | 443 | `62ed91e74829f3a2f6acc6eb34d182fe2ef409849c8ce115e3661c68d2368c54` |
| `docs/RELEASE-INTEGRITY-METHOD.md` | 790 | `b1be17d8d4fae810c9031aa751c0620582f11c506bd912cf2cd302ed475a4d43` |
| `docs/RELEASE-PACK-METHOD.md` | 1060 | `6587fb5098d3e37888ee8e4f3361a7f1ed98399ca2c15dac9e7ec856429e37bb` |
| `docs/REQUIRED-CHECK-GATE-METHOD.md` | 890 | `d0a1a4837b041eafe7befa81d42e778589f60be725c16fefc9e707d9c3704f07` |
| `docs/SECURITY-MODEL.md` | 600 | `aa7791f6af51315671c5e413448f5da23793984dd6642d17364eb4d8128daada` |
| `docs/SEMANTIC-REGRESSION-METHOD.md` | 799 | `f74e9584ec44a1ddb72244a3fb39580df9d7f5bd8358f5b3d1b9882c7b00e790` |
| `docs/SUPPLY-INVARIANT-METHOD.md` | 1060 | `f2cab69df71546bc0dd6913b3b77ff7faa9d3c9c6bf07082a15a6ccc8553cfc7` |
| `docs/TERMUX-WORKFLOW.md` | 535 | `ec3ee5ec1d437e5513e51eec0e57173f1d5a8bafa4069ae9c4c58bccdbd64661` |
| `docs/VERIFICATION-PROFILES.md` | 462 | `a445d5e8bcb05ca53be7351d336de82aba36633c7724d03a8d5d067282385d69` |
| `docs/WVP-RELEASE-REALITY-CAPABILITY-INDEX-V0.1.md` | 2205 | `3c820612168c9e4cc94c416c24b1983e7d74c8decb24c0d68c0c50778377e88c` |
| `docs/WVP-RELEASE-REALITY-CHECK-V0.1.md` | 1737 | `13de50601233c1066664ebed1b2f1be2a4c01e5df5c19e4d8132c6fc5a3f7a22` |
| `docs/adr/0001-release-reality-core-boundary.md` | 793 | `ab84f653fd82e56e48b1cc2cc817f10b3821d2058c61f961dbab1eb1aad09d56` |
| `docs/architecture/WVP-RELEASE-REALITY-ENGINE.md` | 1257 | `3e4bbbdd6bf98846dedfeb9b9237d43878efd24a9f87bc870ddaa55e2b71c75f` |
| `docs/auneya/AUNEYA-CLAIM-SCHEMA-V0.1.md` | 1721 | `2fc9ff11c1e592ddc53808d94194c160e19fae905097fbb8f0254a2f98ea05e2` |
| `docs/auneya/AUNEYA-EVENT-SCHEMA-V0.1.md` | 2002 | `827465edbe6c84809f1a2f75c742b9fa18a83a3c653daca3253a764c49cd15cf` |
| `docs/auneya/AUNEYA-LOCAL-CLAIM-SELECTION-V0.1.md` | 2046 | `dc9648403532d0309ea8d90b0e90f381d6897d56e56fab0ef1606fb111e6be60` |
| `docs/auneya/AUNEYA-LOCAL-COLLECT-COMMAND-V0.1.md` | 1977 | `da8385fe2041032e02be58bb1344acaa8a6a5e44bba033a035676ea7dd803872` |
| `docs/auneya/AUNEYA-LOCAL-COLLECTION-LEDGER-SIMULATION-V0.1.md` | 2259 | `cbf9d6524e4544c1a496130adcf101c8e463a74f5557bb24dfc19b680e5e98b9` |
| `docs/auneya/AUNEYA-LOCAL-COLLECTION-STATUS-DISPLAY-V0.1.md` | 1604 | `cc77f0e288381467cad7953172e9c27500e81677f67ee1d2dcdf6b9f54eb6de7` |
| `docs/auneya/AUNEYA-LOCAL-DEMO-QUICKSTART-V0.1.md` | 2374 | `2e1f673155004260b84c18c33f94e6b58b232d0baf539216f8d3d1b4e02af13e` |
| `docs/auneya/AUNEYA-LOCAL-WITNESS-CLI-DISPLAY-V0.1.md` | 1491 | `5caaa0d8de1f9217b504518b4bfa8304c89cab08af0b0e1b855fcec1f9d63069` |
| `docs/auneya/AUNEYA-LOCAL-WITNESS-RUNNER-V0.1.md` | 1332 | `268dfcfb2e224a88d4f33cccc52820b952f5736791d9ecc70562ec402b3c71dd` |
| `docs/auneya/AUNEYA-MINIMAL-FAIR-GENESIS-LAUNCH-PATH-V0.1.md` | 5483 | `4a9d744a0e141c2d3913178701c133e91ce855c014361c1c2ba430bd4fe61691` |
| `docs/auneya/AUNEYA-NON-VALUE-SIMULATION-NOTICE.md` | 812 | `b6949091e632c606705bc243a9fb1c946b9c98380a2918189326aed82bc3a4fc` |
| `docs/auneya/AUNEYA-ONE-COMMAND-LOCAL-DEMO-V0.1.md` | 1307 | `90159b9c84049e990cec71c39a55f6ea3029cd5c2a9f4eaa4b07730cf1baa4a9` |
| `docs/auneya/AUNEYA-PROTOCOL-CHARTER.md` | 3048 | `4c41a081f71d473cab160e0f0b51de4bdb5e304d5cbd5364cdd90f97c3996a5b` |
| `docs/auneya/AUNEYA-PROVABLE-WEB-SCOPE.md` | 2086 | `55b3d40054a1d6283269bf688f593d24b69a8f9c1d8485dad7a555f0ceb09071` |
| `docs/auneya/AUNEYA-PULSE-AND-PROOFLET-FLOW-V0.1.md` | 2016 | `6fc1ed642c55c76f21f036f2a5196966f0fec7798f585fcf0b2f78f8e43b6c27` |
| `docs/auneya/AUNEYA-WITNESS-PROOF-SCHEMA-V0.1.md` | 1903 | `cba41a922d86f388e48242f029d08c919cc5c5432c376bb98dcf818bd8d497e7` |
| `docs/auneya/README.md` | 5552 | `949caeaae0b2103d8faf1dd34d9a3f47d80a585d7dc9bc6c7e8e051a04179f40` |
| `docs/core/EVIDENCE-MODEL.md` | 531 | `9fc5920f7e41c030c4ccef161f85e1aaaaa2c3f73a0863c5da2475484aae2ec5` |
| `docs/release-check/WVP-ADVERSARIAL-CLASSIFICATION-INVARIANTS.md` | 1399 | `aabe1aa90a9abe03770fa54d774d39214de632f44733930ce79cb7d21bdaabca` |
| `docs/release-check/WVP-REPORT-V1-COMPATIBILITY-GUARD.md` | 1035 | `74194083a952888eeac5ae816ce063bb483cb0b9cb6d91ffca746176e0a4398e` |
| `docs/release-check/WVP-STABLE-JSON-REPORT-CONTRACT.md` | 917 | `e9195c2fb547ab0da4025a2a10f6d91e52caad5ccc6c0636372635071beb4b7d` |
| `docs/release-check/WVP-V040-CAPABILITIES-AND-USAGE.md` | 5583 | `a165e6b09a9a81a54b7ac361404d5df3846a94b2447b15f557bba75958cfb43d` |
| `docs/release-check/WVP-V040-CONTROLLED-RELEASE-PLAN.md` | 3796 | `56f54baa6c70d2712f9afbfabb29956f68fe80b2b84464ce34055a4dfbb92afa` |
| `docs/release-check/WVP-V040-FINAL-PRE-RELEASE-GATE.md` | 3593 | `02382563848eab94cc08f22de50a07a0074318a9ed8186f8acfa4908a469700d` |
| `docs/release-check/WVP-V040-FIXTURE-RUNNER-DESIGN.md` | 2634 | `14805ea36d12c2c659fd62e4d839c228a17953138c9b8e182ae157786fd68dbe` |
| `docs/release-check/WVP-V040-PRE-RELEASE-PREP-STOP-MARKER.md` | 2543 | `1f43c772207053ff4c392d7e527e67d992d84c358b144d261d1e6ca0972bad59` |
| `docs/release-check/WVP-V040-RELEASE-NOTES-DRAFT.md` | 3703 | `55938a438dd9ee1f2ae1fd56959c3650474fbc020d6b44b07ee8fc61df25898a` |
| `docs/release-check/WVP-V040-RELEASE-READINESS-CHECKLIST.md` | 3370 | `9cbe7f20203282b225c2231d87774ca37f59be32783a815a343e0700d185f77e` |
| `docs/release-check/WVP-V041-ADVERSARIAL-FIXTURE-MATRIX.md` | 1519 | `1302a4159627cd38e09cabfe55465afeb3e6d7bd34f1158b82a9e4963b2aec82` |
| `docs/release/ANDROID-VS-CI-BUILD-EVIDENCE-2026-10-05.md` | 2779 | `5fb81468288ecf319d89706cae4404bdf9ba6bb08d0ff887c37926fb19e9fc60` |
| `docs/release/CI-BUILD-PROVENANCE-ARTIFACTS.md` | 1821 | `6964f78ce91562eb88ebaf87b4481bdbe9bf364d2f35abd86f4dfafcefb9bd4e` |
| `docs/release/INDEPENDENT-ENVIRONMENT-EVIDENCE-SEPARATION.md` | 2697 | `3b554790c4e3e4e70a9829b12a46f0aae6694aba42cbdbc26b39fb2bb2648d3e` |
| `docs/release/LINUX-VS-ANDROID-BUILD-EVIDENCE-COMPARISON-FORMAT.md` | 3077 | `539507f13a3bb839b33e5d8832d8ec8a17e7048f6f75a1b4b6298ee3c1ec278f` |
| `docs/release/RELEASE-CONFORMANCE-BASELINE.md` | 950 | `11fb064d96affd4aac89e4db76ee54360c7670e48fe809a52ba143d0c98ff2f2` |
| `docs/release/RELEASE-SIGNING-KEY-POLICY.md` | 1044 | `079bbb8ed2287fd99e4a1d243a9e9619551971b2b24348021b3dba6999f32839` |
| `docs/release/REPRODUCIBLE-BUILD-EVIDENCE-MODEL.md` | 2341 | `398ba1fcb3e8344a5daac67bdc5800dd124c30928e5a8b77159fce178f17b759` |
| `docs/release/SAME-ENVIRONMENT-REPEAT-BUILD-COMPARISON.md` | 1685 | `fe435667ac260a9ce8007af8451afa51453a38398c3519d859fc60935d840769` |
| `docs/release/SELF-VERIFICATION-RELEASE-POLICY.md` | 509 | `beb9481ec2ca4c4d693955c939768ef9ef114149d95932dd5738cfb88d3653ab` |
| `docs/release/SIGNATURE-ARTIFACT-POLICY.md` | 1266 | `c543b320abdfffedb818d145c9cecaf8a06f206d5cef3dcc1099245b479555fc` |
| `docs/release/SIGNATURE-ASSET-MATCHING.md` | 939 | `1e8d8cef8de2da9088baab29edf8937989f9bd223f7c2bd8561f02f26611fada` |
| `docs/release/SIGNATURE-STATUS-MODEL.md` | 955 | `372464d9eff7472c129a14b760e932eb88bcd5e9fbd619405d8c2381a5a34065` |
| `docs/release/SIGNATURE-TAMPER-NEGATIVE-TESTING.md` | 953 | `a8bb53b2527ce61f9b45c6f3c596aa9bf895f4481d2fb3439c5360035a227580` |
| `docs/release/SIGNATURE-TOOLING-CAPABILITY.md` | 1336 | `78b0f68bc430dd1f2e2861eda06189e2a5857ab41b35bfb64b8ad35ce37a973d` |
| `docs/release/SIGNATURE-VERIFICATION-EXECUTION.md` | 1325 | `cf23117aaf7511fa0b197380f6159079c7bcde31833ad2e64bfc7296537073aa` |
| `docs/release/SIGNATURE-VERIFICATION-IMPLEMENTATION-PATH.md` | 1055 | `0aebc68c64ba039cb21cc2a2b7ff7ba3227b70130014f75975e5b1dfd3254481` |
| `docs/release/WVP-V0.3-ARTIFACT-NAMING-PLAN.md` | 1891 | `8a53e98597fb3c83452d273234e171fe11d8912eb6e4eb05ae9fee292219ff34` |
| `docs/release/WVP-V0.3-DETACHED-SIGNATURE-PROCEDURE.md` | 2362 | `2f25cebe82e5c567ca86697d16951d49b29200d205fbcbd0c572425e07ff4993` |
| `docs/release/WVP-V0.3-LOCAL-SIGNING-EXECUTION-GUARD.md` | 2163 | `72f27aa6fe5eee6cc0e864b6e536238f9cb5b0056900a46e2b283250e3fefb77` |
| `docs/release/WVP-V0.3-POST-RELEASE-VERIFICATION.md` | 1489 | `482ec3f4236e8c7262d2a9588601923cb65a397fcfe3803a64077f231f041798` |
| `docs/release/WVP-V0.3-RELEASE-NOTES-DRAFT.md` | 2123 | `bffc1380cbd23195754592aeab772ae777b4823775a8302f5b190286aa1d4ee8` |
| `docs/release/WVP-V0.3-RELEASE-PUBLICATION-GUARD.md` | 2228 | `8945fd05e0e9c102174e6c62c4be6b3f30d9eeb8eacbd2ab46566740a83e3477` |
| `docs/release/WVP-V0.3-RELEASE-READINESS-CHECKLIST.md` | 2929 | `ec4251aadb0dd0aa3618a452c2e838ae8d2e953b4276b52560f21270bd26db3e` |
| `docs/release/WVP-V0.3-UNSIGNED-ASSET-STAGING.md` | 1968 | `99f9da4faf78ec7050ae5021bcc9033218b79890a2b6025a59196eeead5ab4d0` |
| `docs/release/WVP-V0.3-VERSION-BUMP-AND-RELEASE-COMMAND-PLAN.md` | 4645 | `5f1920cb57ccf60f0615a1604fc88003969de7a06a3612597d5457a9bcff0066` |
| `docs/release/WVP-v0.2-RELEASE-BUILD-PROCEDURE.md` | 1546 | `ff9b9d03c7757420ead766400e612be716e99e88aa7895b93acd69df7c9e4257` |
| `docs/release/WVP-v0.2-RELEASE-CANDIDATE.md` | 2490 | `d1417615adb4dfdb3693b7265354c1b199884571738353c040db1b2f0f5b7c7f` |
| `docs/release/WVP-v0.2-RELEASE-CHECKLIST.md` | 2649 | `170d1407d1955f77431290053ee5b709e7f789e65547a38d69dc56b13e558f92` |
| `docs/release/WVP-v0.2.0-POST-RELEASE-VERIFICATION.md` | 1774 | `f8e71ad1228ec7d60643585eca0081f010da39059c274e9891e6398c411c7a1d` |
| `docs/release/WVP-v0.3-REPRODUCIBLE-BUILD-EVIDENCE-PLAN.md` | 1204 | `6766abec5b28cb81cfbd00045995254c42673b933ba0f9df477124801c6bd6c8` |
| `docs/review/WVP-RELEASE-REALITY-REVIEW-CHECKLIST.md` | 706 | `0372624d2e9e0a49ba3d8047cf16ade4a0b669700ec5c4978be75c001796e2bf` |
| `docs/roadmap/WVP-V0.4-RELEASE-CHECK-FIXTURE-STRATEGY.md` | 3292 | `c2a19b9351cb9ea5cb43f45bdba6e39f89789a727909e7462537ff83fa2e8354` |
| `docs/roadmap/WVP-V0.4-RELEASE-CHECK-HARDENING-MATRIX.md` | 4580 | `a757c885bd24ae1c5520037b8b26df16e4c8b84edd91e349653bbaeddbd91a8d` |
| `docs/roadmap/WVP-V0.4-SCOPE-AND-PLAN.md` | 4135 | `431ce6ee8c70cd2e9c0e0260a4236e4191ef12e6188e9d92579c3538e5d57005` |
| `docs/schemas/wvp-release-check-report-v1.schema.json` | 2937 | `a84ce309766244009aedcf737d3b22156e5447c3d19e7d6f4979078fb26643d0` |
| `docs/threat-model/WVP-RELEASE-REALITY-THREAT-MODEL.md` | 913 | `9967e0e3924aefa3a5550315b927d0c3714c07f63b9975976d410e0219a0648c` |
| `fuzz/nightfall/v1.0.5/README.md` | 495 | `2ff03ffcf31a91b203fc30fd26fc9ff5a0c11ecfc49aba54dfe9367e5c184ee3` |
| `negative-vectors/nightfall/v1.0.5/nv-cons-001-immature_coinbase_spend.json` | 692 | `cfece0703e7b5875734719de5f742531e88b6893622a6cac296ace00a8eb7d66` |
| `negative-vectors/nightfall/v1.0.5/nv-cons-002-duplicate_input.json` | 674 | `dfed93e5cc63bbcf401f1ea9c8fd42552dd1038792a223937fb00a3e732bbbc2` |
| `negative-vectors/nightfall/v1.0.5/nv-cons-003-unsorted_block_body.json` | 679 | `b508231e68f9e389997a82d6c2ef8c76af72cc9ecb800dcecfc1833b04b4516a` |
| `negative-vectors/nightfall/v1.0.5/nv-cons-004-block_apply_atomicity_case.json` | 714 | `2749e1a5dd2b358452f1ae62b6b3287648553b561d4cf821e89950de90e84545` |
| `negative-vectors/nightfall/v1.0.5/nv-inf-001-thin_air_mint.json` | 679 | `8963004ed81cf5667707ec9fc99d3d06f96e68b754979ae6d42b60193e843418` |
| `negative-vectors/nightfall/v1.0.5/nv-inf-002-negative_amount_attempt.json` | 697 | `925901d91a9d070656b28ec1ac9928a94903ac371889dae048779ac2ecae9b32` |
| `negative-vectors/nightfall/v1.0.5/nv-inf-003-invalid_kernel_excess.json` | 686 | `6944ac9ca3bcaf46d2af043bf15616f14a2f096e00223bc2e17b2bbb45cd4d0a` |
| `negative-vectors/nightfall/v1.0.5/nv-pol-001-fee_burn_mismatch.json` | 693 | `1792ce888c222f7e44bcc2dd47078f23a8421b127c5821026258980fc89c3e2a` |
| `negative-vectors/nightfall/v1.0.5/nv-rel-001-release_digest_missing.json` | 686 | `070c683db1b0c473847b57590b763c27da6312beffe513e5f2c7d577d6537cd9` |
| `negative-vectors/nightfall/v1.0.5/nv-theft-001-fake_input_spend.json` | 686 | `a2586620dcddf534ca8006a3e7cecdcda7fa33f89b786e1e928b0d395d42e3d4` |
| `negative-vectors/nightfall/v1.0.5/nv-wallet-001-light_client_lie.json` | 721 | `b441735d7d772e249738e15e77de90cb05e61e331598915e8e83104090282595` |
| `reports/nightfall/v1.0.5/CI-HARDENING.json` | 3719 | `97c0485a0e1335e356d1215bdddbf4b6985a194f04134640ba0cb213973dc9c0` |
| `reports/nightfall/v1.0.5/CI-HARDENING.md` | 2106 | `be51670a1b4b1bc8adb33cc050cf8dc3f6fbda6e360158041c1d0fa9f52779b0` |
| `reports/nightfall/v1.0.5/CODEPATH-BINDINGS.json` | 13782 | `2d513989b09d59e83b64abc7362713e3307c280f281cd82a5e152719e7dec3a3` |
| `reports/nightfall/v1.0.5/CODEPATH-BINDINGS.md` | 4058 | `a9c348dc15e8ab903cd5d3b2ff365a6f6e1c8d22eb96b6f5f1ef544bf27179e5` |
| `reports/nightfall/v1.0.5/COMMAND-PROBES.json` | 36619 | `311273b1120b1801e53cdb96cf8484e353688a0aa15fdc3b400809c32f62a451` |
| `reports/nightfall/v1.0.5/COMMAND-PROBES.md` | 14739 | `2f124bf442c0b6915d2e522e1612c142f7efe9379c9d3b066310a6bf84a4273a` |
| `reports/nightfall/v1.0.5/CONFORMANCE-SCORE.json` | 6862 | `e1b7d197c529063eba41ad0bd68589f49fe7f4f55da97b76c6fb10e7c05e6d1b` |
| `reports/nightfall/v1.0.5/CONFORMANCE-SCORE.md` | 1206 | `c31e5312b991669a8140c3a98028e836227512c41b7f9df093f89f9753ea4f6c` |
| `reports/nightfall/v1.0.5/FINDINGS-TRIAGE.json` | 4898 | `8d78504d6c18aef0135a27a4a46f6ac5e2e9765cfa2307abbf8e67a96ea53c9e` |
| `reports/nightfall/v1.0.5/FINDINGS-TRIAGE.md` | 2707 | `af2c0931473818544f5e867546d0038f062bf6480c885da0afa72d80d61b72a9` |
| `reports/nightfall/v1.0.5/FINDINGS.md` | 672 | `9c3e7c60e54d5bf3c91c3a5ac024fc5872358224618d80d11ae6371fabe39d5b` |
| `reports/nightfall/v1.0.5/LIMITATIONS.md` | 484 | `4645ed96a0d8dc0e6d5ac9945c2b42ce16d23398ee85822c4fe3c5eb2f8d2769` |
| `reports/nightfall/v1.0.5/NEGATIVE-VECTORS.json` | 4867 | `a391993a6262b4f4ac57750cf705864afae5decdd47c77d5fec2944614b56e2c` |
| `reports/nightfall/v1.0.5/NEGATIVE-VECTORS.md` | 3511 | `5bc448c1f0ac112073b740e067f3201d94fe4d972d1bf1da5e8dd257872a1adb` |
| `reports/nightfall/v1.0.5/PUBLIC-REPORT.md` | 1537 | `383664d405bb3a5ac6a95bfe20cc4d3af985af09f24142fad95a28153a7d372a` |
| `reports/nightfall/v1.0.5/RELEASE-INTEGRITY.json` | 37684 | `90a1791615caee71cc0f73d2136406413b5024cde1ae5a1c4d58974fb00885fe` |
| `reports/nightfall/v1.0.5/RELEASE-INTEGRITY.md` | 14833 | `0e5ebabc32801ff83d1f76e5387486acb10db99093930e1e78b92e30919c08a0` |
| `reports/nightfall/v1.0.5/RUNBOOK.md` | 236 | `acd91aae50a096547193b3f70cd0210d0cf2f968a27a2de97b5b88d4b15c9714` |
| `reports/nightfall/v1.0.5/SECURITY-REVIEW-PLAN.md` | 568 | `43b99dbd30c3b40da831fc46de8ec3961664b4bb64e6f1f91b8eedc09a705219` |
| `reports/nightfall/v1.0.5/SEMANTIC-REGRESSION.json` | 5960 | `db81aab0662569f3a9e7b5102c2e8fa22bce0b261d5502a2b03c8421e21948d3` |
| `reports/nightfall/v1.0.5/SEMANTIC-REGRESSION.md` | 4536 | `5fba988f9e3091b900b4487fbf40617b6dcda9999bd2af034fa4a3927abdf9f3` |
| `reports/nightfall/v1.0.5/SUPPLY-INVARIANT-MAP.json` | 142783 | `9355e14ac445a985fc21b7976d2fd597d2b73d8078870cc86be3015c68e56eb5` |
| `reports/nightfall/v1.0.5/SUPPLY-INVARIANT-MAP.md` | 8411 | `86297e6e533f602fa70fe22576dc527bc6c8032ffe3cb729fb6f77b6fdf41f76` |
| `reports/nightfall/v1.0.5/TRACEABILITY.md` | 835 | `8d8465260c9f5c30a9f4d1deab473f61cbaffd2e59af60dbaf2d90c0fb7c97ca` |
| `templates/github/branch-protection-required-checks.json` | 501 | `567e3cf6dca470b0a84153d9abb4617834cc3ba6b8b1a7ab81db9735b9c85c1c` |
| `templates/github/required-checks.md` | 238 | `6066be24cc50648cc7a9270795d54970700fc2609a85e080f96830d1df288cc6` |
| `templates/security/finding-record.json` | 459 | `1313e209a1a92b74807ebf24900554f4cf38ad9bba51f4adaac55c24b02d703e` |
| `templates/security/private-disclosure-checklist.md` | 461 | `a868cacf2c3babebe3f41682e51a470914d1bd73b09f0d0921daaa0975f96b01` |
| `templates/security/sanitized-finding.md` | 490 | `3a5fd065a013a693666649c5e8c0e4131aa8a881b2b76df6e1c0794487abe57c` |
| `tests/test_ci_hardening.py` | 2010 | `c910b177b184f793bf26c095ad0a380ef89f4767ba821bed5bddd41bc816356a` |
| `tests/test_codepath_bindings.py` | 927 | `0269dc46c111664272d3f6ea219327c87992ebfdca612e3a20f85831b38c3ed3` |
| `tests/test_command_probes.py` | 1022 | `33f915f4bc7981ae0bb41dd4b68169ecc15e813e926de6993970c4ef4c5ade15` |
| `tests/test_conformance_score.py` | 1521 | `0c84a5de686b8c9293962dce8bdf8e36bb0b099d13df5714037ed8b467c063c7` |
| `tests/test_negative_vectors.py` | 1598 | `178b5de878468b6c93b66e5000dd725d6e6e16850a23515f8829d44af3cef411` |
| `tests/test_nightfall_verifier.py` | 1144 | `230efced57b370d0542bf09c24ad2636e54460f77e409d2acb5c7adbf0a42f3a` |
| `tests/test_release_integrity.py` | 1347 | `89a6561ad5890c08181eaa22e17c6a991dba3818db79973081e16c6f47d203da` |
| `tests/test_release_pack.py` | 1676 | `e3e21f064996206718fa87eead624fc8880b2415250191645cd2fa60f786b3d7` |
| `tests/test_semantic_regression.py` | 1122 | `68fc701f884cb77eca865ee9bb5938977fd3b972908c68b78d8b7ceca93ef1e3` |
| `tests/test_supply_invariant.py` | 1311 | `bf0b508121cd0a8c227d08740b374a1a27a90cfff85791f20287609c7bca26e4` |
| `tests/test_triage_workflow.py` | 1904 | `f5dcfefd85403342dcfcdc4e82546dc3a6961e836c5b3219c08f60482a064311` |
| `wvp/nightfall/ci_hardening.py` | 2919 | `e3c29e56be31d6bfacc03c78fb38a597a4b6a325970cf0381ab5337b9e9c523a` |
| `wvp/nightfall/codepath_binding.py` | 803 | `cf2e9b659994a10f2f8b883e5a9eea5e93c563e46e02f54d958f3ccdb8deb35a` |
| `wvp/nightfall/command_probes.py` | 947 | `778c0a4314fe3a934b45c9b0b2d829f67e53c128ff7e28d1b755641e5e7877d3` |
| `wvp/nightfall/conformance_score.py` | 1975 | `175f1d22cc2eb5483ba0bd199fbd63288ef0bf43551cfc23e8aabf82601de5dc` |
| `wvp/nightfall/negative_vectors.py` | 2170 | `64a2134c9a6b0f5ae5d9f40d9e4daf927fb462707f825f2adc5faf3b69c5ee5b` |
| `wvp/nightfall/release_integrity.py` | 1265 | `651f6f9963b0aa3c1feb0dca3d3b90158963bd155e3276176e8cfde8b9c10fce` |
| `wvp/nightfall/release_pack.py` | 2373 | `8acffa2e4fef38ae92a08c60db917023d458c6e7467656551dc0a0bb5e0d38a2` |
| `wvp/nightfall/semantic_regression.py` | 993 | `edfc083ade5e3cc8482a458f5b84a80757ece989d577170e4fef26c82d50caae` |
| `wvp/nightfall/supply_invariant.py` | 1495 | `b43e930025b8da84c8a8407bd61739d38df87e9e6f2b7a2d1b9679fb81a21ea7` |
| `wvp/nightfall/triage_workflow.py` | 2416 | `551966288817b13c1e025701f265fe9ac2e3fd229cf3f77017342fa27dba2c8d` |
| `wvp/nightfall/verifier.py` | 3250 | `e8e84c59c184c62a7ffd5f1c4a3fe26de3f92fd41fa3051bd827700b638378dc` |

## Non-audit boundary

This bundle packages WVP evidence only. It does not prove implementation correctness, cryptographic soundness, production safety, or audit status.
