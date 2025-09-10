# Side chain analogues

We find ~1.1k side-chain analogues for asp, lys, phe, ser, thr, tyr, glu. Most of these are for threonine (ethanol) (451 properties). Most of these are densities (826). There are 293 enthalpies of mixing.

The notebook has the code used to generate the CSV. The analogue SMILES are pasted below.


```
SIDE_CHAIN_ANALOGS = {
    "ala": "C",
    "val": "CCC",
    "leu": "CC(C)C",
    "ile": "CCCC",
    "met": "CCSC",
    "phe": "Cc1ccccc1",
    "trp": "CC1=CNC2=CC=CC=C12",
    "hid": "CC1=CN=CN1",
    "hie": "CC1N=CNC=1",
    "lys": "CCCCN",
    "arg": "CCCNC(=N)N",
    "asp": "CC(=O)O",
    "glu": "CCC(=O)O",
    "ser": "CO",
    "thr": "CCO",
    "cys": "CS",
    "tyr": "Cc1ccc(O)cc1",
    "asn": "CC(=O)N",
    "gln": "CCC(=O)N",
}
```