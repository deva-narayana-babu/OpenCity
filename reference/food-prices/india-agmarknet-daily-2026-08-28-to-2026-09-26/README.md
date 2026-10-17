# Agmarknet daily prices: Surat and Ahmedabad districts (28 Aug to 26 Sep 2026)

These are daily market-wise commodity arrivals and prices (minimum, maximum and modal) for every Agricultural Produce Market Committee (APMC) that Agmarknet lists under Surat and Ahmedabad districts.

- **Publisher:** Directorate of Marketing & Inspection (Agmarknet), Ministry of Agriculture & Farmers Welfare, Government of India.
- **Endpoint:** `POST https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily`. It is undocumented and is the one the agmarknet.gov.in site itself uses.
- **Request body:** `{"date": "YYYY-MM-DD", "marketIds": [...], "stateIds": [11], "includeExcel": false}`.
- **Headers:** `Content-Type: application/json`, `Origin: https://agmarknet.gov.in`, `Referer: https://agmarknet.gov.in/`.
- **Market IDs:** listed per district in [market-ids.json](market-ids.json). Agmarknet's "Surat" list also includes markets in Tapi district (Songadh, Vyara, Uchhal, Nizar, Kukarmunda, Valod).
- **Files:** `<District>_<YYYY-MM-DD>.json` holds one raw response per district per day, unmodified. Fetched on 27 Sep 2026.

## Reporting coverage (computed from these files)

| Main market | Days with price rows | Days with none |
|---|---|---|
| Surat APMC | 23 of 30 | 2026-08-28, 2026-08-30, 2026-09-04, 2026-09-06, 2026-09-13, 2026-09-20, 2026-09-25 |
| Ahmedabad APMC | 21 of 30 | 2026-08-28, 2026-08-30, 2026-09-04, 2026-09-06, 2026-09-13, 2026-09-15, 2026-09-20, 2026-09-22, 2026-09-26 |

A market with no price rows is either absent from the response or returns "NIL Transaction - No Arrivals".

## Checksums

| File | sha256 |
|---|---|
| Ahmedabad_2026-08-28.json | `d5af7aa7b93501dfe39d75ba9e04015439de83f704e4045fd78b1075a6d1977f` |
| Ahmedabad_2026-08-29.json | `506959fdec9df087e18ed20d11c10b96cb8b47a3e922bf8a6f7859d8b4940b3c` |
| Ahmedabad_2026-08-30.json | `0f592c5e252548fe7b48f3c3e9d4070d74c4d27ff01fc56a720364c1f0c6f86b` |
| Ahmedabad_2026-08-31.json | `c4b1b38bc7462c6519716a1f3e27a2e5ed52c37b0b850d002f89f4a0c9e364d8` |
| Ahmedabad_2026-09-01.json | `39f84fc4fbbc6c2704ff98fc870551cf579d9eda0df9cf8af83c1459c62d7291` |
| Ahmedabad_2026-09-02.json | `02b5d041fdb8851e327c905ae864d4e295d0a3360da0c33a0e21235881d7d6bb` |
| Ahmedabad_2026-09-03.json | `7c307753fdbf86cefebf975a7882df4e86ee5d75bcb5a34bd78e60220300d554` |
| Ahmedabad_2026-09-04.json | `988f43597b6372a91f32bd9f0e300d498a05a88a3b599101c5467f0e3c78b10a` |
| Ahmedabad_2026-09-05.json | `9b2d0a06fcdc02868e636d0b36da9fd8c97079f3bdb69ebe9a08e4e3e9c6ac9f` |
| Ahmedabad_2026-09-06.json | `fa3ce8261c4605e166f28693dea31ef777008fb33cb050878abc0c3e5e95b273` |
| Ahmedabad_2026-09-07.json | `b79c0144d99ce4b3b1ac8252eca6f65d0afedba19ead549864faae7dd619d82c` |
| Ahmedabad_2026-09-08.json | `56911b2da481c4fd8b4b2e58604cd03f6f269397aecd51ff18241963aea00ae2` |
| Ahmedabad_2026-09-09.json | `bbc3423a2b774e512822b63932a391b60c5012be25b73b9599204dc7466d0430` |
| Ahmedabad_2026-09-10.json | `4ecd65acf9dfcc06de35858f0113a8599eb373d426c1c99dac1b99191e459b3e` |
| Ahmedabad_2026-09-11.json | `89ad43d30875254bd59018de23c8563e51f7766cad527b0769454609cbfdddf8` |
| Ahmedabad_2026-09-12.json | `951b725b276232f6745cb650284b2ff13d9c5580accf709408f3b4f4cd24066a` |
| Ahmedabad_2026-09-13.json | `7804bb5262d65f00850ff32c8b58a1682ed38c9518e054e44e104aa39f27232b` |
| Ahmedabad_2026-09-14.json | `085189f1784726c34f89feb93a45af9ccb6004614b391ed62e6b206613cf66f2` |
| Ahmedabad_2026-09-15.json | `1524a9de552fc65cfaf2ead35e02bc3f04b563696c818149dec3db4d3968990c` |
| Ahmedabad_2026-09-16.json | `f12f6be72fcb66393bed983324db22ecfda2e23bdc9cef1db2bfa7edb21b6ab9` |
| Ahmedabad_2026-09-17.json | `96824a3b6f626fd6e5f7772948a30216742fac1e1d7fdc89fc3b21603532b311` |
| Ahmedabad_2026-09-18.json | `1ad318a4d80bc79094b4cb1a7c23b3bc30bfcf37332d8b83a411a7c5f2974d91` |
| Ahmedabad_2026-09-19.json | `e41edb60058af8fad428b3629486026b207253629315d50cad666f5d25b0dc30` |
| Ahmedabad_2026-09-20.json | `775bb434abed1e11dd9a0112c980760207cb1390faa20f78d06327edbf06dacb` |
| Ahmedabad_2026-09-21.json | `119d39228dd65761b2a3babd42577aa72693ea0fede95a4567f1944e67355a50` |
| Ahmedabad_2026-09-22.json | `d61d7968265d08186014f37f89dbbfab7af2ea2501104a1b4106e94600ad5597` |
| Ahmedabad_2026-09-23.json | `ac9b70a9c0dbada62c6d9df2f02a0661df59c53d0e4840f0720486589c1a5150` |
| Ahmedabad_2026-09-24.json | `962d8714469387a3c728701302263edb9b4979e376071dcf01e1286f20598d5d` |
| Ahmedabad_2026-09-25.json | `0c9aeee23b0d0e2aa282dc61c5c24b647517d8d016733d716339331f39df8d10` |
| Ahmedabad_2026-09-26.json | `32519cd2ced71853a5ec8e4ae636014ebc942636d905367c45befd8c89c51439` |
| Surat_2026-08-28.json | `38b1c56fd9a636d1e3149a8c5b6e9fba174140faa767f43ed37584e760dc7d8f` |
| Surat_2026-08-29.json | `d84aef7f4e64463ba29fc94183b3461f4829accf79806eaff0e49e47104828e8` |
| Surat_2026-08-30.json | `c00845ea7fd8ae32de47c03dfe94742f1cf3a90f48d4e8b4f1ee92f8ea287bf8` |
| Surat_2026-08-31.json | `1e5a89e8072030fbf234b377bfb8f65057119bba8a22a7cb93742a3c7756be45` |
| Surat_2026-09-01.json | `8f359aa60f5f4015c0ecfc8390108d3e54922c008eb3cbb9ddaa6804d647ce58` |
| Surat_2026-09-02.json | `9623bc9719d6b76993a11271fec7cb2f304c83d6ea024dc5bec0c5ae56fd31ad` |
| Surat_2026-09-03.json | `c936ef526c6ea5ca26aaddd564182575896d813a0b2cc263852a4129909095f4` |
| Surat_2026-09-04.json | `79d65b9ad36e2b17fd7bb0cf2fbee2783755808dbcb3a82be1f1b80cc83cba8f` |
| Surat_2026-09-05.json | `f5e42390c2dbc4c4626a1af79266c5c2a9fdefda84d16d57e7476aafbbf44922` |
| Surat_2026-09-06.json | `c8b6ce6f5f0553a344ccc1e5a65a49e4ebaa92ffcbfe968f40fdc25c4d0cf4e8` |
| Surat_2026-09-07.json | `856a2d63c6f25549b8b272c3de5f5e2521223304ca0d8fdcfa87e9c521214862` |
| Surat_2026-09-08.json | `eb9f68ac95de537f130b9f21a8ca7ba533045d4f221dd604dd79287906378847` |
| Surat_2026-09-09.json | `936d453b0b41fdd64763662887f0cfa7923b35f01ae96e37ef9ccf7da26817e9` |
| Surat_2026-09-10.json | `41b80b9efc6cd74c734698cddfaeeba596293f221282267e1f6b0963d611bf36` |
| Surat_2026-09-11.json | `47221f1096e489b324bea1ee420e5b8e454ea258b634bb04c1dafe4396d335fc` |
| Surat_2026-09-12.json | `31e13809ef34b0a46b410c12e7760caef6b7ca144f3c06089e17d40ee0495e03` |
| Surat_2026-09-13.json | `9e821a7ca5961edcdf0abaa5d761803c59b777177303e737bc58193f9847f58c` |
| Surat_2026-09-14.json | `22ab11a820496d3a4ab368fbab1f7b219d01d02dccfbcae5f660d3c427d11c5f` |
| Surat_2026-09-15.json | `56a22d9fbca2c2cf1d576b651d5d53c17b7bb67de9b9c38fd3dff40d6a424823` |
| Surat_2026-09-16.json | `ba9c5b6202d66019b9713263390d00560bee5e946009168768f2402d24d27f90` |
| Surat_2026-09-17.json | `0be1688c90160be5fdbdc1922c495304e62bfc458d0fa26e479a04e4d19c209d` |
| Surat_2026-09-18.json | `761616584c6a8737923c06ac4df8c19fdcb92f6509b72a2e74c10a5cbdfc42e0` |
| Surat_2026-09-19.json | `47567fded464f4e56c18b4c21c6438bfc8bb8e9bcffe27eed5d931203b061b31` |
| Surat_2026-09-20.json | `42bf67e0698754ca4a7968aecf76c7847149b24d459c3d1a97ffe364b7e7ae61` |
| Surat_2026-09-21.json | `d0e4667b7aad78c4ebf20d3830abd480a2dafd08f69b3b4865e653aada9da3b2` |
| Surat_2026-09-22.json | `940c5c1a72d58fe0072c5fcfb3e515d44c6d94cc4f5bfdde375256791cfb875b` |
| Surat_2026-09-23.json | `ef9ca475426422df142b326548ee50a2ec531675d906df6316afd796b5c30b32` |
| Surat_2026-09-24.json | `c3ec519138d6394e14e755bc0b3a4778d9cae16cc4ec7ab57e66061a1f070763` |
| Surat_2026-09-25.json | `8129c2bb0d3136cac1ddf31f975079349488e0f17f848461d43e47d089255291` |
| Surat_2026-09-26.json | `8cd642d4769c4dc4f6404529f7221c9305632373e2967fa613fbc188dbb603eb` |
| market-ids.json | `ede5ed0d686e56ab2d5d1e750b28356c710449e3d941348a1c1acd570e8ff861` |
