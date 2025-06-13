#!/bin/bash

rsync -arv -P iris:/data1/choderaj/wangl14/ash-sage/02_fit-vdw/refit/*.* .
rsync -arv -P iris:/data1/choderaj/wangl14/ash-sage/02_fit-vdw/refit/stored_data .