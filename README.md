# Sentry project rerouting
An extension to Sentry that allows rerouting of an event's project before it is saved

## Edits to Sentry source
The latest this change can occur is in the `dispatch` function in `web/api.py`. Therefore, in order to change the project of an event before it's saved, a hook needs to be created that allows plugins to affect this function. I propose a change to the dispatch function that iterates through each enabled plugin and runs their `dispatch` function. `plugins/base/v1.py` also has to be changed to add the `dispatch` function to the base plugin class.

## The Plugin
This pilot plugin for the concept, currently entitled event-router, is used for ROS. If an event includes a tag entitled "node\_name", reffering to the ROS node, the event will be routed to a project under that node name, creating said project if it doesn't exist yet.
