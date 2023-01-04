# oneos_upgrader

Ansible role for upgrading **Ekinops OneAccess** devices running **OneOS** software. There are 2 main OS version: OneOS 5 + OneOS 6.  

OneOS 5 is very similar to Cisco IOS-XE and the software image should be present in the flash and a boot command is required to indicate which software should be loaded.

OneOS 6 has primary + redundant software banks and each bank may have a different software loaded. You have to indicate which bank should be the primary before reloading the router.

This role supports both versions automatically.

## Role tags

There are 4 tags that you can use to define the mode of the role:

- report: does pre-checks and reports the current status and software compliancy
- staging: does pre-checks and software installs but no post-checks or reboots
- reboot: reboots and does post-upgrade checks but without pre-checks are staging, to be used if you have done the staging beforehand
- upgrade (default): combines staging + reboot

## Default role variables

The following variables are configured by default but may be overriden if needed:

- auto_configure_pre_requisites: toggles auto-configuration of pre-requisites (ex enable SCP server) DEFAULT = true

## Calculated variables

The following variables will be calculated based ont he given variables and running config:

- running_os_is_compliant: indicates if the running OS is already compliant or not (compared to wanted_os_version)
- boot_os_is_compliant: indicates if the boot os is already compliant or not (compared to wanted_boot_version)
- scp_is_enabled: indicates if SCP is enabled or not

## Upgrade process

Depending on the tags, the upgrade process may be different. By default a **full upgrade** will be done.

### Report mode

In **report mode** we will only do some basic checks and generate a report which indicates if the router should be upgraded and if there is sufficient disk space.

Usage:

```shell
ansible-playbook -i hosts playbook.yml --tags report
```

Playbook tasks:

- connect and get facts
- set extra facts to determine the status of the router and upgrade process
- display a debug message for each host

Details:

- tasks:
- oneos_upgrader : GATHER FACTS > hostname  TAGS: [always]
- oneos_upgrader : GATHER FACTS > get system details        TAGS: [always]
- oneos_upgrader : GATHER FACTS > get ssh details   TAGS: [always]
- oneos_upgrader : SET FACT > get wanted os file stats      TAGS: [always]
- oneos_upgrader : SET FACT > wanted_os_file_stats  TAGS: [always]
- oneos_upgrader : SET FACT > get wanted boot file stats    TAGS: [always]
- oneos_upgrader : SET FACT > wanted_boot_file_stats        TAGS: [always]
- oneos_upgrader : SET FACT > get wanted recovery file stats        TAGS: [always]
- oneos_upgrader : SET FACT > wanted_recovery_file_stats    TAGS: [always]
- oneos_upgrader : GATHER FACTS > show memory       TAGS: [always]
- oneos_upgrader : SET FACT > fact_memory   TAGS: [always]
- oneos_upgrader : MAIN > run os specific gather_facts tasks        TAGS: [report, staging, upgrade]
- oneos_upgrader : SET FACT > calculate if upgrades are required    TAGS: [always]
- oneos_upgrader : SET FACT > scp_is_enabled        TAGS: [always]
- oneos_upgrader : SET FACT > check if the files exist on disk or software bank     TAGS: [always]
- oneos_upgrader : SET FACT > file upload requirement       TAGS: [always]
- oneos_upgrader : SET FACT > recovery_file_exists_on_disk  TAGS: [always]
- oneos_upgrader : SET FACT > disk_space_sufficient_ facts calculation      TAGS: [always]
- oneos_upgrader : REPORT > get host details        TAGS: [report, staging, upgrade]
- DEBUG > output all variables      TAGS: [always]
- Template a file to /etc/file.conf TAGS: [always]

> A template is foreseen to generate an overview CSV report, since this is supposed to run as last task in the play, it has to be called from within the playbook.

```ansible
  post_tasks:
    - name: REPORT > save to file
      ansible.builtin.template:
        src: "roles/oneos_upgrader/templates/report_overview.j2"
        dest: report.txt
      tags:
        - always
```

### Staging mode

In **staging mode** all the necessary checks are done and all files are uploaded and the upgrade is being prepared without causing any interruptions.

Usage:

```shell
ansible-playbook -i hosts playbook.yml --tags staging
```

Playbook tasks:

- connect and get facts
- set extra facts to determine the status of the router and upgrade process
- if there is no space on the device then old files will be removed
- if there are any pre-config jobs then they will be implemented (ex enable SCP)
- upload files if needed
  - if there is no space for all files then first the boot files will be copied
- the software bank or the boot file is being prepared IF there are no pending boot image upgrades

> If multiple upgrades are required (BOOT + RECOVERY + OS) then it's not possible to stage everything at the same time. If there is enough disk space for all files then the upload will be finished. The loading of the file can only be done on the first file (ex BOOT) because it requires are reboot in order to continue. So multi-stage upgrades should be done step by step or the extra steps will be performed during the upgrade process.
