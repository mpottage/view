#!/usr/bin/python3

# Copyright Matthew Pottage 2016
# Chooses view_image or view_folder as appropriate for the query.
# See view_common.py.
import view_common as common
import view_folder
import view_image

query_path = common.raw_query_path();
if common.is_image(query_path):
    view_image.main()
else:
    view_folder.main()
