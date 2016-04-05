# sentry-event-router
An extension to Sentry that allows rerouting of an event's project before it is saved

## Edits to Sentry source
In order to change the project of an event before it's saved, a hook needs to be created that allows plugins to affect the `dispatch` function in `web/api.py`. I propose a change to the dispatch function that iterates through each enabled plugin and runs their `dispatch` function

## The Plugin
This pilot plugin for the concept is used for ROS. If an event includes a tag entitled "node\_name", reffering to the ROS node, the event will be routed to a project under that node name, creating said project if it doesn't exist yet.
