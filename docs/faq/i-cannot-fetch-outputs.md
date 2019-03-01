---
title: "I was able to see job's outputs but I am not able to see them anymore."
meta_title: "I am getting Bad Request when trying to fetch outputs using the web UI or using the CLI - FAQ"
meta_description: "Polyaxon provides several ways for storing the outputs, the default method uses a local path on the host node."
featured: false
custom_excerpt: "Polyaxon provides several ways for storing the outputs, the default method uses a local path on the host node."
author:
  name: "Polyaxon"
  slug: "Polyaxon"
  website: "https://polyaxon.com"
  twitter: "polyaxonAI"
  github: "polyaxon"
visibility: public
status: published
tags:
    - logging
---

Polyaxon provides several ways for storing the [outputs](/configuration/custom-outputs-storage/), the default method uses a local path on the host node. 
This is option is sufficient if you are trying the platform and don't want to deal with extra configuration steps, however, when using Polyaxon in a production mode, 
you should definitely look at the other persistence strategies.

When the user uses a local path to store outputs, a couple of things could happen:
 * If you have more than one node, i.e. using other nodes to schedule experiments and jobs, you will not be able to see the outputs, because they will be stored on the node where the experiment/job was scheduled.
 * The host node might be deleted, or replaced, and all outputs will be deleted as well.
 * If the user scales the platform, the API, scheduler, and other component might be deployed on different nodes, which means that only some of these components will be able to access the outputs.
 * If the API is replicated on different node same thing could happen as well.
 * After an upgrade all your component might be scheduled on a different node.
 
Polyaxon provides several options to make robust persistent of your outputs.   
