```sh

$ source venv/bin/activate
$ ./delete.py

[+] Processing input file input.yaml

[+] Generating terraform file tf/aws/terraform.tfvars

[+] Detected infrastructure provider: aws

[+] Destroying infrastructure on provider aws

[+] Switching to  directory tf/aws to destroy infrastructure

------ TERRAFORM OUTPUT ----------

Destroy complete! Resources: 10 destroyed.

[+] Switching back to directory /Users/rgill/testbeds/eksa-bm-vbox

[+] Detected cluster provisioner: native

[+] Deleting gateway & cluster on provisioner native
```