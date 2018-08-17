## Creating an environment for testing OSG app integration:

**Note:** The following commands worked on one of our server 

- Make directory

```
$ mkdir osg-gl-upendra && cd osg-gl-upendra
```

- Create a HT Path List input file (`input-paths2.txt`) that contains 2 files on DE and then move it using icommand

```
$ iget -PVT /iplant/home/input-paths2.txt
```

- Look at the contents of the input HT-path list file. Make sure to remove the header after you download the input file.

```
$ cat input-paths2.txt
/iplant/home/upendra_35/osg-gl-upendra/TE_RNA_transcripts.fa
/iplant/home/upendra_35/osg-gl-upendra/sample.fa
```

- Create a output path file on the data store

```
$ cat output-paths2.txt
/iplant/home/upendra_35/osgwc-test-upendra/output
```

- Create tickets using `create-tickets.sh` script

- Create input tickets

```
$ ./create-tickets.sh -r input-paths2.txt > input_ticket.list
$ cat input_ticket.list
# application/vnd.de.path-list+csv; version=1
afd6bf6705754041b3e092781bf406,/iplant/home/upendra_35/osg-gl-upendra/TE_RNA_transcripts.fa
0ae99494c79d451d8bcea3bcce86ae,/iplant/home/upendra_35/osg-gl-upendra/sample.fa
```

- Create output tickets

```
$ ./create-tickets.sh -w output-paths2.txt > output_ticket.list
$ cat output_ticket.list
# application/vnd.de.path-list+csv; version=1
3c38859a83ed4aee85417d657e386d,/iplant/home/upendra_35/osg-gl-upendra/output
```

- Create a config file

```
$ cat config.json
{
  "arguments": [
    "sample.fa",
    "TE_RNA_transcripts.fa"
  ],
  "irods_host": "davos.cyverse.org",
  "irods_port": 1247,
  "irods_job_user": "upendra_35",
  "irods_user_name": "job",
  "irods_zone_name": "",
  "input_ticket_list": "input_ticket.list",
  "output_ticket_list": "output_ticket.list",
  "status_update_url": "https://de.cyverse.org/job/bd1a1b53-9a7e-4031-bf0c-227a0c63f555/status",
  "stdout": "out.txt",
  "stderr": "err.txt"
}
```

- Create a wrapper script for testing with the input files

``` 
$ cat wrappertest.py

#!/usr/bin/env python

import re
import sys

from get_gene_length_filter import get_gene_lengths

if __name__ == "__main__":
    for input_file in sys.argv[1:]:
        output_file = re.sub(r"[.][^.]+$", ".txt", input_file)
        with open(input_file, "rU") as fh_in, open(output_file, "w") as fh_out:
            get_gene_lengths(fh_in, fh_out) 
```

```
$ cat get_gene_length_filter.py
#!/usr/bin/env python

import sys

def get_gene_lengths(fh_in, fh_out):
    genes = {}

    gene_name = ""
    for line in fh_in:
        line = line.strip()
        if line[0] == ">":
            gene_name = line[1:]
            genes[gene_name] = 0
        elif gene_name != "":
            genes[gene_name] += len(line)

    for (name,val) in genes.items():
        print >>fh_out, "{0}\t{1}".format(name, val)
```

- Test wrapper script

```
python2.7 wrappertest.py files/sample.fa files/TE_RNA_transcripts.fa
```

- Create a Dockerfile

```
FROM ubuntu:xenial

RUN mkdir /cvmfs /work
WORKDIR /work

# Install some prerequisites.
RUN apt-get update \
    && apt-get install -y lsb wget apt-transport-https python2.7 python-requests

# Install icommands.
RUN wget -qO - https://packages.irods.org/irods-signing-key.asc | apt-key add - \
    && echo "deb [arch=amd64] https://packages.irods.org/apt/ xenial main" > /etc/apt/sources.list.d/renci-irods.list \
    && apt-get update \
    && apt-get install -y irods-icommands

# Install the wrapper script.
ADD wrapper /usr/bin/wrapper
ADD get_gene_length_filter.py /usr/bin/get_gene_length_filter.py
RUN chmod +x /usr/bin/get_gene_length_filter.py

# Make the wrapper script the default command.
CMD ["wrapper"]
```

- Build docker image

```
$ docker build -t osggl:1.0 .
```

- Test your docker image

```
$ docker run --rm -v ${PWD}:/data -w /data osggl:1.0
```

- Push your docker image to Dockerhub

- Pull your docker image and test again

```
docker run --rm -v ${PWD}:/data -w /data cyverse/osg-gl:1.0
```

- Do a PR on OSG [github repo](https://github.com/opensciencegrid/cvmfs-singularity-sync)

- After PR is merged, it takes 1-2 hours for the image to show up in CVFMS and after which you can import the tool and let one of DE team know that it is OSG app (this will change in future)

- Create the app in DE 
