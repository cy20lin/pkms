# User Stories

> As a ADJECTIVES ROLE, i want WHAT, so that WHY

## US-0001

As a PKMS owner and user,
I want to be able to own my knowledges and files resources on my achievable/controllalbe devices,
so that I can trust and access the resources on my trustable device/endpoint without worries.

## US-0002

As a PKMS owner and user,
I want to be able reference the file resource with its identity,
such identity will hardly change in the scope of the system lifetime,
so that I can ALWAYS use that identity to refer to that specific resource,
no matter how the content change and/or the file title in file name changes, file location changes, as long as the file is under PKMS government.

take markdown for example, one could link other md page via markdown link, the reference is constructed with a caption and a path to the file. e.g. `[Caption of a cool Image](/path/to/image.png)`, once the path changes, the link in fails. and maintain such links in files become tidious. the linked file may change due to rearrangement of the directory structure, file renaming for better description, and such scenerio is an anti-pattern or a PKMS user

take obsidian for example, in obsidian. One is able to link via wiki link, the wikilink is made of the file name the user want to linked to. e.g. `[[WikiLink Target Filename]]` while such approach solve the issue of path changes of the target file, but if one change the filename

##

as a user
i'd like to be able to install the URI Handler to the OS
so that the pkms uri could be resolved to the target resource
maybe view in browser, show in explorer, open in dedicated app assigned by OS.

##

as a user
when viewing the files in the web browser,
i want to be able to increase/decrease the importance of that file,
so that importance of the file could be updated.
and maybe the search result could be respecting the importance
maybe also want to be able to add context comment on that file as well.
