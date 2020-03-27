Import-Module ActiveDirectory
#queries all computer accounts in an AD security group , selects their FQDN and Description fields, outputs to computers.csv file. 
Get-ADGroupMember *security group* -Server *your domain*| Where-Object {$_.objectClass -eq "computer"} | get-adcomputer -prop DNSHostname, Description | Select-Object DNSHostname,Description | export-csv -Path .\computers.csv -NoTypeInformation
#run the adgrp2asa script to compile and push commands.
python .\adgrp2asa.py