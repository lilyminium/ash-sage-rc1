2.3.0-v2 is `fb-fit-v2-single-mean-eps.offxml`; `fb-fit-v2-single-mean-eps-with-am1bcc.offxml` is identical but has a `<ToolkitAM1BCC>` tag to workaround a bug in pontibus 0.0.2 in which an absent `<ToolkitAM1BCC>` tag causes system prep to fail.


```sh
micromamba create -f gen_charges_env.yml
micromamba run -n pontibus_gen_charges python gen_charges.py

micromamba create -f ../alchemiscale-client.yml

cd freesolv
micromamba run -n pontibus_everything_bagel python gen_network.py
micromamba run -n pontibus_everything_bagel python ../shared-scripts/submit.py --network_filename alchemical_network.json --org_scope "openff" --scope_name_campaign "openff_2_3_0_v2" --scope_name_project "freesolv" --repeats 3
cd ..

cd mnsol
micromamba run -n pontibus_everything_bagel python gen_network.py
micromamba run -n pontibus_everything_bagel python ../shared-scripts/submit.py --network_filename alchemical_network.json --org_scope "openff" --scope_name_campaign "openff_2_3_0_v2" --scope_name_project "mnsol" --repeats 3
cd ..

cd highrmse
micromamba run -n pontibus_everything_bagel python gen_network.py
micromamba run -n pontibus_everything_bagel python ../shared-scripts/submit.py --network_filename alchemical_network.json --org_scope "openff" --scope_name_campaign "openff_2_3_0_v2" --scope_name_project "highrmse" --repeats 3
cd ..

micromamba run -n pontibus_everything_bagel python shared-scripts/monitor.py --scope_key mnsol-oe/scoped-key.dat
```
